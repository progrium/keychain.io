from StringIO import StringIO
import unittest

from keychain.app import app
from keychain.app import keys

TEST_KEY = """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC1sUFNQQj51hKbKcAkEd/FmWvk8Hao+YHFLWX9iDTbwFUX6zZjjiTScoOpzsjHiN8tY4sOcBWcFGctPlLfGGkcD6gxdvUtOiU4/kyJ0RG1Pz2HcUz4wqWzWpXqH1q/sAujxZDV3iRzl6U5KwqrVLUuHp1C+TZGMFzvEdsSy2ISQmRY09wNH7km7TxOz9w9iRrfk49BVv8hGr2/VU2U+34u1n7Ebusp5JaLlJM6AqhlvFaHhuiNG4+7dhKLzLMb9A6+BEKMMEKARxHckFRhH7DhnDaz1UH84dXex+Cq/+z6bDeHWvs5mAG+6ET7qz8sRxWpQGupOqV/lMo58Mw22ZBL test@example.com"""

class KeychainTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        keys.clear()

    def test_root(self):
        rv = self.app.get('/')
        assert rv.status_code == 302

    def test_default_key_get(self):
        rv = self.app.get('/nobody@example.com')
        assert rv.status_code == 404

        keys['test@example.com']['default'] = TEST_KEY
        rv = self.app.get('/test@example.com')
        assert TEST_KEY in rv.data

    def test_default_key_put(self):
        rv = self.app.put('/test@example.com', data={
            'key': (StringIO(TEST_KEY), 'id_rsa.pub'),})
        assert rv.status_code == 200
        assert TEST_KEY in keys['test@example.com']['default']
        
    def test_default_key_delete(self):
        keys['test@example.com']['default'] = TEST_KEY
        rv = self.app.delete('/test@example.com')
        assert rv.status_code == 200

        rv = self.app.get('/test@example.com')
        assert rv.status_code == 404

    def test_default_actions(self):
        rv1 = self.app.get('/test@example.com/upload')
        rv2 = self.app.get('/test@example.com/default/upload')
        assert rv1.data == rv2.data
    
        rv1 = self.app.get('/test@example.com/install')
        rv2 = self.app.get('/test@example.com/default/install')
        assert rv1.data == rv2.data

        keys['test@example.com']['default'] = TEST_KEY
        rv1 = self.app.get('/test@example.com/fingerprint')
        rv2 = self.app.get('/test@example.com/default/fingerprint')
        assert rv1.data == rv2.data

    def test_all_get(self):
        test_key1 = TEST_KEY.replace('test@example.com', 'testkey1')
        test_key2 = TEST_KEY.replace('test@example.com', 'testkey2')
        keys['test@example.com']['a'] = test_key1
        keys['test@example.com']['b'] = test_key2
        rv = self.app.get('/test@example.com/all')
        assert test_key1 in rv.data
        assert test_key2 in rv.data

    def test_all_install(self):
        test_key1 = TEST_KEY.replace('test@example.com', 'testkey1')
        test_key2 = TEST_KEY.replace('test@example.com', 'testkey2')
        keys['test@example.com']['a'] = test_key1
        keys['test@example.com']['b'] = test_key2
        rv = self.app.get('/test@example.com/all/install')
        assert test_key1 in rv.data
        assert test_key2 in rv.data

    def test_named_key_get(self):
        rv = self.app.get('/nobody@example.com/github')
        assert rv.status_code == 404

        keys['test@example.com']['github'] = TEST_KEY
        rv = self.app.get('/test@example.com/github')
        assert TEST_KEY in rv.data

    def test_named_key_put(self):
        rv = self.app.put('/test@example.com/github', data={
            'key': (StringIO(TEST_KEY), 'id_rsa.pub'),})
        assert rv.status_code == 200
        assert TEST_KEY in keys['test@example.com']['github']
        
    def test_named_key_delete(self):
        keys['test@example.com']['github'] = TEST_KEY
        rv = self.app.delete('/test@example.com/github')
        assert rv.status_code == 200

        rv = self.app.get('/test@example.com/github')
        assert rv.status_code == 404
