import socket
import pickle
import threading


class NetworkHandler:
    """Handles all network communication between client and server"""

    def __init__(self):
        self.socket = None  # The network socket
        self.connected = False  # Connection status
        self.player_symbol = None  # 'X' or 'O' assigned by server
        self.callbacks = []  # Functions to call when receiving data

    def connect_to_server(self, host='localhost', port=5555):
        """Establish connection to the game server"""
        try:
            # Create a TCP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to the server
            self.socket.connect((host, port))
            self.connected = True

            # First receive the player symbol (X or O) as string
            self.player_symbol = self.socket.recv(1024).decode()
            print(f"Connected as Player {self.player_symbol}")

            # Start a background thread to continuously receive data
            # This prevents the game from freezing while waiting for network data
            thread = threading.Thread(target=self.receive_data)
            thread.daemon = True  # Thread closes when main program exits
            thread.start()

            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def receive_data(self):
        """Background thread function - continuously listens for server updates"""
        while self.connected:
            try:
                # Wait for data from server (blocks until data arrives)
                data = self.socket.recv(4096)
                if not data:
                    break  # Connection closed

                # Convert bytes back to Python object (dictionary)
                game_state = pickle.loads(data)

                # Call all registered callback functions with the new state
                for callback in self.callbacks:
                    callback(game_state)

            except Exception as e:
                print(f"Receive error: {e}")
                break

    def send_move(self, position):
        """Send a move to the server"""
        if self.connected:
            try:
                # Convert position to string and send as bytes
                self.socket.send(str(position).encode())
                return True
            except:
                return False
        return False

    def disconnect(self):
        """Close the network connection"""
        self.connected = False
        if self.socket:
            self.socket.close()

    def add_callback(self, callback):
        """Register a function to be called when game state updates"""
        self.callbacks.append(callback)