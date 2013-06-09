import collections
import base64
import uuid
import hashlib

from flask import Flask
from flask import request
from flask import redirect
from flask import render_template

app = Flask('keychain')
app.config['DEBUG'] = True

keys = collections.defaultdict(dict)
pending_actions = {}

def lookup_key(email, name=None):
    name = name or 'default'
    if email in keys and name in keys[email]:
        return keys[email][name]

def upload_key(email, name, key):
    keys[email][name] = key.strip()

def delete_key(email, name):
    del keys[email][name]

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
    pass

def send_confirmation(action, token, email):
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
    keys_ = [lookup_key(email, key) for key in keys[email]]
    return "{0}\n".format('\n'.join(keys_))

@app.route('/<email>/all/install')
def all_install(email):
    keys_ = [lookup_key(email, key) for key in keys[email]]
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


