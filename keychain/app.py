import base64
import uuid
import hashlib
import os

import eventlet
import requests
import boto
import boto.s3.key
from boto.s3.connection import OrdinaryCallingFormat, Location

from flask import Flask
from flask import request
from flask import redirect
from flask import render_template

app = Flask('keychain')
app.config['DEBUG'] = True

bucket_name = os.environ.get('KEYCHAIN_BUCKET_NAME')
bucket_location = os.environ.get('KEYCHAIN_BUCKET_LOCATION', Location.DEFAULT)
action_expiry = 3600
pending_actions = {}

s3 = None

def s3key(email, name):
    global s3
    if not s3:
        s3 = boto.connect_s3(calling_format=OrdinaryCallingFormat())
    k = boto.s3.key.Key(
        s3.create_bucket(bucket_name, location=bucket_location))
    k.key = '{}.{}'.format(email, name)
    return k

def s3keys(email):
    global s3
    if not s3:
        s3 = boto.connect_s3(calling_format=OrdinaryCallingFormat())
    b = s3.create_bucket(bucket_name, location=bucket_location)
    return b.list(prefix=email)

def lookup_key(email, name=None):
    name = name or 'default'
    k = s3key(email, name)
    try:
        return k.get_contents_as_string()
    except:
        return None

def lookup_keys(email):
    keys = s3keys(email)
    try:
        return [k.get_contents_as_string() for k in keys]
    except Exception, e:
        return None

def upload_key(email, name, key):
    k = s3key(email, name)
    k.set_contents_from_string(key.strip())

def delete_key(email, name):
    k = s3key(email, name)
    k.delete()

def fingerprint(keystring):
    key = base64.b64decode(keystring.split(' ')[1])
    fp = hashlib.md5(key).hexdigest()
    return ':'.join(a+b for a,b in zip(fp[::2], fp[1::2]))

def confirm_key_upload(email, keyname, key):
    token = str(uuid.uuid4())
    pending_actions[token] = (upload_key, (email, keyname, key))
    schedule_action_expiration(token)
    send_confirmation('upload', token, email)

def confirm_key_delete(email, keyname):
    token = str(uuid.uuid4())
    pending_actions[token] = (delete_key, (email, keyname))
    schedule_action_expiration(token)
    send_confirmation('delete', token, email)

def schedule_action_expiration(token):
    eventlet.spawn_after(action_expiry, lambda: pending_actions.pop(token, None))

def send_confirmation(action, token, email):
    if 'SENDGRID_USERNAME' in os.environ:
        requests.post("https://sendgrid.com/api/mail.send.json",
            data={
                'api_user':os.environ.get('SENDGRID_USERNAME'),
                'api_key':os.environ.get('SENDGRID_PASSWORD'),
                'to':email,
                'subject':"Keychain.io {} Confirmation".format(action.capitalize()),
                'from':"robot@keychain.io",
                'text':"Click this link to confirm {}:\n{}{}/confirm/{}".format(
                    action, request.url_root, email, token)})
    else:
        print("Email to {} for {}: {}{}/confirm/{}".format(
            email, action, request.url_root, email, token))

@app.route('/')
def index():
    return redirect("http://github.com/progrium/keychain.io")

@app.route('/<email>/confirm/<token>')
def confirm_action(email, token):
    if token not in pending_actions:
        return "Action expired\n"
    else:
        action = pending_actions.pop(token)
        action[0](*action[1])
        return "Action completed\n"

@app.route('/<email>', methods=['GET', 'PUT', 'DELETE'])
def default_key(email):
    return named_key(email, 'default')

@app.route('/<email>/upload')
def default_upload(email):
    return named_key_action(email, 'default', 'upload')

@app.route('/<email>/install')
def default_install(email):
    return named_key_action(email, 'default', 'install')

@app.route('/<email>/fingerprint')
def default_fingerprint(email):
    return named_key_action(email, 'default', 'fingerprint')

@app.route('/<email>/all')
def all_keys(email):
    keys_ = lookup_keys(email)
    return "{0}\n".format('\n'.join(keys_))

@app.route('/<email>/all/install')
def all_install(email):
    keys_ = lookup_keys(email)
    return render_template('install.sh', keys=keys_)

@app.route('/<email>/<keyname>', methods=['GET', 'PUT', 'DELETE'])
def named_key(email, keyname):
    if request.method == 'PUT':
        key = request.files.get('key')
        if key:
            confirm_key_upload(email, keyname, key.read())
            return "Key received, check email to confirm upload.\n"
        else:
            return "No key specified\n", 400

    elif request.method == 'GET':
        key = lookup_key(email, keyname)
        if key:
            return "{0}\n".format(key)
        else:
            return "Key not found\n", 404

    elif request.method == 'DELETE':
        key = lookup_key(email, keyname)
        if key:
            confirm_key_delete(email, keyname)
            return "Check your email to confirm key deletion.\n"
        else:
            return "Key not found\n", 404

@app.route('/<email>/<keyname>/<action>')
def named_key_action(email, keyname, action):
    if action == 'fingerprint':
        key = lookup_key(email, keyname)
        if key:
            return fingerprint(key)
        else:
            return "Key not found\n", 404

    elif action == 'upload':
        keypath = request.args.get('keypath', '')
        url_root = request.url_root
        return render_template('upload.sh', email=email,
                keyname=keyname, keypath=keypath, url_root=url_root)

    elif action == 'install':
        key = lookup_key(email, keyname)
        if key:
            return render_template('install.sh', keys=[key])
        else:
            return 'echo "No key to install."'
