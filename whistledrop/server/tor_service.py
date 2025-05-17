import os
import logging
from stem.control import Controller
from stem import Signal, SocketError

class TorService:
    def __init__(self, tor_control_port=9051, web_port=5000, hidden_service_dir=None):
        """
        Initialize the Tor service.
        
        Args:
            tor_control_port: The port Tor's control interface is listening on (default: 9051)
            web_port: The port the Flask application will run on (default: 5000)
            hidden_service_dir: Directory to store hidden service data (default: None - uses Tor default)
        """
        self.tor_control_port = tor_control_port
        self.web_port = web_port
        self.controller = None
        self.hidden_service_dir = hidden_service_dir or os.path.join(os.path.expanduser('~'), '.tor', 'whistledrop_service')
        self.onion_address = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('tor_service')

    def start(self):
        """Start the Tor service and create a hidden service."""
        try:
            self.connect()
            self.onion_address = self.create_hidden_service(self.web_port)
            self.logger.info(f"Hidden service running at: {self.onion_address}.onion")
            return self.onion_address
        except Exception as e:
            self.logger.error(f"Error starting Tor service: {e}")
            return None

    def connect(self):
        """Connect to the Tor control port."""
        try:
            self.controller = Controller.from_port(port=self.tor_control_port)
            
            # You may need to use a password or cookie file for authentication
            # This depends on your Tor configuration
            try:
                self.controller.authenticate()
                self.logger.info("Connected to Tor control port (no auth)")
            except Exception:
                # Try using cookie file authentication if direct auth fails
                cookie_path = os.path.join(os.path.expanduser('~'), '.tor', 'control_auth_cookie')
                if os.path.exists(cookie_path):
                    with open(cookie_path, 'rb') as f:
                        cookie = f.read()
                    self.controller.authenticate(cookie)
                    self.logger.info("Connected to Tor control port (cookie auth)")
                else:
                    self.logger.error("Could not authenticate with Tor control port")
                    raise

            self.logger.info(f"Connected to Tor version {self.controller.get_version()}")
        except SocketError as e:
            self.logger.error(f"Tor control connection failed: {e}")
            self.logger.error("Make sure Tor is running and ControlPort is enabled in torrc")
            raise

    def create_hidden_service(self, port):
        """
        Create a Tor hidden service that forwards to the specified port.
        
        Args:
            port: The local port to forward Tor traffic to
            
        Returns:
            The .onion address (without the .onion suffix)
        """
        if not self.controller:
            raise Exception("Not connected to Tor control port")
            
        # Create hidden service directory if it doesn't exist
        os.makedirs(self.hidden_service_dir, exist_ok=True)
        
        # Check if we already have a hidden service
        existing_services = self.controller.list_ephemeral_hidden_services()
        if existing_services:
            for service in existing_services:
                self.logger.info(f"Removing existing hidden service: {service}")
                self.controller.remove_ephemeral_hidden_service(service)
        
        # Create a new ephemeral hidden service
        # The service maps remote port 80 to the local web_port where the Flask app is running
        response = self.controller.create_ephemeral_hidden_service(
            {80: f"127.0.0.1:{port}"},
            await_publication=True,
            detached=True
        )
        
        onion_address = response.service_id
        self.logger.info(f"Created hidden service at {onion_address}.onion")
        
        # Save the onion address to a file for reference
        with open(os.path.join(self.hidden_service_dir, 'hostname'), 'w') as f:
            f.write(f"{onion_address}.onion")
            
        return onion_address

    def signal_reboot(self):
        """Sends a signal to Tor to clean circuits and fetch new Tor nodes."""
        if self.controller:
            self.logger.info("Sending NEWNYM signal to Tor")
            self.controller.signal(Signal.NEWNYM)
            return True
        return False

    def close(self):
        """Close the connection to the Tor control port."""
        if self.controller:
            if self.onion_address:
                # Remove the ephemeral hidden service
                try:
                    self.controller.remove_ephemeral_hidden_service(self.onion_address)
                    self.logger.info(f"Removed hidden service: {self.onion_address}.onion")
                except Exception as e:
                    self.logger.error(f"Error removing hidden service: {e}")
            
            self.controller.close()
            self.controller = None
            self.logger.info("Closed connection to Tor control port")