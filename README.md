# keychain.io

Bash
----
Upload your default SSH key:

    curl -s ssh.keychain.io/<email>/upload | bash

Install your key into authorized_keys:

    curl -s ssh.keychain.io/<email>/install | bash

URLS
----
    ssh.keychain.io/<email>
    ssh.keychain.io/<email>/upload
    ssh.keychain.io/<email>/install
    ssh.keychain.io/<email>/fingerprint
    ssh.keychain.io/<email>/confirm/<token>
    ssh.keychain.io/<email>/all
    ssh.keychain.io/<email>/all/install
    ssh.keychain.io/<email>/<namedkey>
    ssh.keychain.io/<email>/<namedkey>/fingerprint
    ssh.keychain.io/<email>/<namedkey>/install
    ssh.keychain.io/<email>/<namedkey>/upload

Contributing
------------
You will need to create a new S3 bucket

Either clone this repository or fork and clone, then install dependencies

    git clone git@github.com:RyanBalfanz/keychain.io.git
    pip install -r requirements.txt

Create a .env file, so that foreman will populate the appropriate environment variables when you start the server with `foreman start`

    $ cat .env
    AWS_ACCESS_KEY_ID=abc123
    AWS_SECRET_ACCESS_KEY=abcd1234
    SENDGRID_USERNAME=ryan
    SENDGRID_PASSWORD=password
    BUCKET_NAME=keychain.io

Finally, start the application

    foreman start
