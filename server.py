import socket
import threading
import pickle
from game import TicTacToe


class GameServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(2)
        self.players = []  # List of (connection, address, symbol)
        self.game = TicTacToe()
        self.current_turn = 0  # 0 for X, 1 for O
        self.game_started = False
        print(f"Server started on {host}:{port}")
        print("Waiting for 2 players...")

    def broadcast(self):
        """Send game state to all connected players"""
        for i, (conn, addr, symbol) in enumerate(self.players):
            game_data = {
                'board': self.game.board,
                'current_player': self.game.current_player,
                'winner': self.game.winner,
                'game_over': self.game.game_over,
                'your_symbol': symbol,
                'your_turn': (i == self.current_turn),
                'game_started': self.game_started
            }
            try:
                conn.send(pickle.dumps(game_data))
            except:
                pass

    def handle_client(self, conn, addr, player_index):
        symbol = 'X' if player_index == 0 else 'O'
        self.players.append((conn, addr, symbol))

        # Send player symbol first
        conn.send(symbol.encode())
        print(f"Player {symbol} connected from {addr}")

        # If we have 2 players, start the game
        if len(self.players) == 2:
            self.game_started = True
            print("\n" + "=" * 50)
            print("GAME STARTED! Both players connected.")
            print(f"Player X: {self.players[0][1]}")
            print(f"Player O: {self.players[1][1]}")
            print("Player X goes first!")
            print("=" * 50 + "\n")
            self.broadcast()

        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                position = int(data.decode())
                print(f"Player {symbol} moved to {position}")

                # Check if it's this player's turn
                if player_index == self.current_turn and not self.game.game_over:
                    if self.game.make_move(position):
                        self.current_turn = 1 - self.current_turn
                        self.broadcast()

                        if self.game.game_over:
                            print(f"Game Over! Winner: {self.game.winner}")
                            self.broadcast()

            except Exception as e:
                print(f"Error: {e}")
                break

        print(f"Player {symbol} disconnected")
        self.players.remove((conn, addr, symbol))
        conn.close()

    def start(self):
        try:
            while len(self.players) < 2:
                conn, addr = self.server.accept()
                player_index = len(self.players)
                thread = threading.Thread(target=self.handle_client, args=(conn, addr, player_index))
                thread.daemon = True
                thread.start()

            # Keep server running
            while True:
                threading.Event().wait(1)

        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            self.server.close()


if __name__ == "__main__":
    server = GameServer()
    server.start()