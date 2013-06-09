TODO
----
* use s3
* confirmation emails
* readme

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
