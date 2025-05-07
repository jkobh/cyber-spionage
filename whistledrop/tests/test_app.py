import unittest
from server.app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'WhistleDrop', response.data)  # TODO: Update with actual content check

    def test_upload_page(self):
        response = self.app.get('/upload')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Upload File', response.data)  # TODO: Update with actual content check

    # TODO: Add more tests for other routes and functionalities

if __name__ == '__main__':
    unittest.main()