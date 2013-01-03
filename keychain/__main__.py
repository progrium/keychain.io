import os

from keychain.app import app

if __name__ == "__main__":
    app.run('0.0.0.0', int(os.environ.get("PORT", 5000)))
