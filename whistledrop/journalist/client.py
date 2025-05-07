class JournalistClient:
    def __init__(self, server_url):
        self.server_url = server_url

    def retrieve_file(self, file_id):
        # TODO: Implement logic to retrieve the encrypted file from the server using the file_id
        pass

    def decrypt_file(self, encrypted_file, private_key):
        # TODO: Implement logic to decrypt the retrieved file using the provided private_key
        pass

    def display_file(self, decrypted_file):
        # TODO: Implement logic to display or save the decrypted file
        pass

# Example usage
if __name__ == "__main__":
    journalist_client = JournalistClient("http://localhost:5000")
    # TODO: Implement command line interface for the journalist to interact with the client
    pass