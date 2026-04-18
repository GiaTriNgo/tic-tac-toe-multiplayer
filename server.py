import socket
import threading
import pickle
from game import TicTacToe


class GameServer:
    """Manages game state and synchronizes between two players"""

    def __init__(self, host='0.0.0.0', port=5555):
        # Create server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reusing the address (prevents "address already in use" errors)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind to all network interfaces on port 5555
        self.server.bind((host, port))
        # Listen for up to 2 connections
        self.server.listen(2)

        # List to store connected players: (connection, address, symbol)
        self.players = []
        # The actual game logic instance
        self.game = TicTacToe()
        # 0 = X's turn, 1 = O's turn
        self.current_turn = 0
        # Flag to track if both players are connected
        self.game_started = False

        print(f"Server started on {host}:{port}")
        print("Waiting for 2 players...")

    def broadcast(self):
        """Send current game state to all connected players"""
        # Iterate through all players with their index
        for i, (conn, addr, symbol) in enumerate(self.players):
            # Create game state dictionary
            game_data = {
                'board': self.game.board,  # Current board state
                'current_player': self.game.current_player,  # X or O
                'winner': self.game.winner,  # Winner if game over
                'game_over': self.game.game_over,  # Game status
                'your_symbol': symbol,  # Player's symbol
                'your_turn': (i == self.current_turn),  # Is it this player's turn?
                'game_started': self.game_started  # Game started flag
            }
            try:
                # Convert dictionary to bytes and send
                conn.send(pickle.dumps(game_data))
            except:
                pass  # Ignore errors (player might have disconnected)

    def handle_client(self, conn, addr, player_index):
        """Handle communication with a single player"""
        # Assign symbol based on connection order (first = X, second = O)
        symbol = 'X' if player_index == 0 else 'O'

        # Store player info
        self.players.append((conn, addr, symbol))

        # Send the player their symbol first
        conn.send(symbol.encode())
        print(f"Player {symbol} connected from {addr}")

        # If this is the second player, start the game
        if len(self.players) == 2:
            self.game_started = True
            print("\n" + "=" * 50)
            print("GAME STARTED! Both players connected.")
            print(f"Player X: {self.players[0][1]}")
            print(f"Player O: {self.players[1][1]}")
            print("Player X goes first!")
            print("=" * 50 + "\n")
            # Send initial game state to both players
            self.broadcast()

        # Main communication loop for this player
        while True:
            try:
                # Wait for move from client
                data = conn.recv(1024)
                if not data:
                    break  # Client disconnected

                # Convert position from string to integer
                position = int(data.decode())
                print(f"Player {symbol} moved to {position}")

                # Validate move: correct player turn and game not over
                if player_index == self.current_turn and not self.game.game_over:
                    # Apply the move to the game
                    if self.game.make_move(position):
                        # Switch to next player's turn
                        self.current_turn = 1 - self.current_turn
                        # Send updated game state to both players
                        self.broadcast()

                        # If game is over, announce winner
                        if self.game.game_over:
                            print(f"Game Over! Winner: {self.game.winner}")
                            self.broadcast()

            except Exception as e:
                print(f"Error: {e}")
                break

        # Clean up when player disconnects
        print(f"Player {symbol} disconnected")
        self.players.remove((conn, addr, symbol))
        conn.close()

    def start(self):
        """Main server loop - accepts connections and creates threads"""
        try:
            # Keep accepting connections until we have 2 players
            while len(self.players) < 2:
                # Accept a new connection
                conn, addr = self.server.accept()
                # Assign player index (0 or 1) based on current count
                player_index = len(self.players)
                # Create a new thread to handle this player
                thread = threading.Thread(target=self.handle_client,
                                          args=(conn, addr, player_index))
                thread.daemon = True
                thread.start()

            # Keep server running after game starts
            # (In a real implementation, you might want to handle multiple games)
            while True:
                threading.Event().wait(1)

        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            self.server.close()


if __name__ == "__main__":
    server = GameServer()
    server.start()