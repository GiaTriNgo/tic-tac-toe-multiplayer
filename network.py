import socket
import pickle
import threading


class NetworkHandler:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.player_symbol = None
        self.callbacks = []

    def connect_to_server(self, host='localhost', port=5555):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True

            # Receive player symbol
            self.player_symbol = self.socket.recv(1024).decode()
            print(f"Connected as Player {self.player_symbol}")

            # Start receiving thread
            thread = threading.Thread(target=self.receive_data)
            thread.daemon = True
            thread.start()

            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def receive_data(self):
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break

                game_state = pickle.loads(data)
                for callback in self.callbacks:
                    callback(game_state)

            except Exception as e:
                print(f"Receive error: {e}")
                break

    def send_move(self, position):
        if self.connected:
            try:
                self.socket.send(str(position).encode())
                return True
            except:
                return False
        return False

    def disconnect(self):
        self.connected = False
        if self.socket:
            self.socket.close()

    def add_callback(self, callback):
        self.callbacks.append(callback)