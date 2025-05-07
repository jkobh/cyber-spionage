import unittest
from server.crypto import encrypt_file, decrypt_file  # TODO: Implement these functions
from io import BytesIO

class TestCrypto(unittest.TestCase):

    def setUp(self):
        # TODO: Set up test data and keys
        self.test_data = b'This is a test file.'
        self.test_key = b'This is a key123'  # Example key, replace with a proper key
        self.test_filename = 'test_file.txt'

    def test_encrypt_file(self):
        # TODO: Implement the encryption test
        encrypted_data = encrypt_file(self.test_data, self.test_key)
        self.assertIsNotNone(encrypted_data)
        self.assertNotEqual(encrypted_data, self.test_data)

    def test_decrypt_file(self):
        # TODO: Implement the decryption test
        encrypted_data = encrypt_file(self.test_data, self.test_key)
        decrypted_data = decrypt_file(encrypted_data, self.test_key)
        self.assertEqual(decrypted_data, self.test_data)

if __name__ == '__main__':
    unittest.main()