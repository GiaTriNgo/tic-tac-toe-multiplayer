import pygame

# TicTacToe class - handles all game rules and logic
class TicTacToe:
    def __init__(self):
        # Board is a list of 9 positions (index 0-8)
        # Empty string '' means empty cell
        self.board = [''] * 9
        # X always starts first
        self.current_player = 'X'
        self.winner = None
        self.game_over = False

    def make_move(self, position):
        """Place current player's symbol on the board if valid"""
        # Check if game is still active and cell is empty
        if not self.game_over and self.board[position] == '':
            # Place the symbol
            self.board[position] = self.current_player
            # Check if this move wins the game
            self.check_winner()
            # If game continues, switch to other player
            if not self.game_over:
                self.switch_player()
            return True
        return False

    def switch_player(self):
        """Alternate between X and O players"""
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def check_winner(self):
        """Check if the current move resulted in a win or tie"""
        # All possible winning combinations (rows, columns, diagonals)
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]

        # Check each winning pattern
        for pattern in win_patterns:
            # If all three positions have the same non-empty symbol
            if (self.board[pattern[0]] and
                    self.board[pattern[0]] == self.board[pattern[1]] == self.board[pattern[2]]):
                self.winner = self.board[pattern[0]]
                self.game_over = True
                return

        # Check for tie (all cells filled with no winner)
        if all(cell != '' for cell in self.board):
            self.game_over = True
            self.winner = 'Tie'

    def reset(self):
        """Reset the game for a new round"""
        self.board = [''] * 9
        self.current_player = 'X'
        self.winner = None
        self.game_over = False


# GameRenderer class - handles all visual drawing
class GameRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.width = 600
        self.height = 700
        self.cell_size = 200  # Each cell is 200x200 pixels

    def draw_board(self, game, player_symbol, your_turn, game_mode='single'):
        """Draw the entire game state on screen"""
        # Fill background with dark gray
        self.screen.fill((30, 30, 30))

        # Draw the 3x3 grid lines
        for i in range(1, 3):
            # Vertical lines
            pygame.draw.line(self.screen, (255, 255, 255),
                             (i * self.cell_size, 0),
                             (i * self.cell_size, self.height - 100), 3)
            # Horizontal lines
            pygame.draw.line(self.screen, (255, 255, 255),
                             (0, i * self.cell_size),
                             (self.width, i * self.cell_size), 3)

        # Draw X's and O's on the board
        font = pygame.font.Font(None, 120)  # Large font for X/O
        for i in range(9):
            if game.board[i]:  # If cell has a symbol
                # Calculate center position of the cell
                x = (i % 3) * self.cell_size + self.cell_size // 2
                y = (i // 3) * self.cell_size + self.cell_size // 2
                # Green for X, Orange for O
                color = (0, 255, 0) if game.board[i] == 'X' else (255, 100, 0)
                # Render and draw the symbol
                text = font.render(game.board[i], True, color)
                text_rect = text.get_rect(center=(x, y))
                self.screen.blit(text, text_rect)

        # Draw status text (turn indicator, game over message)
        font_small = pygame.font.Font(None, 36)
        if game.game_over:
            # Show winner or tie message
            if game.winner == 'Tie':
                status = "Game Over - Tie!"
            else:
                status = f"Game Over - Player {game.winner} wins!"
        else:
            # Show whose turn it is
            if game_mode == 'single':
                # Single player mode - show player or AI turn
                if player_symbol == game.current_player:
                    status = f"Your turn ({player_symbol})"
                else:
                    status = "AI is thinking..."
            else:
                # Multiplayer mode - show player turn
                if your_turn:
                    status = f"Your turn ({player_symbol})"
                else:
                    status = f"Opponent's turn ({game.current_player})"

        # Draw status text at bottom of screen
        status_text = font_small.render(status, True, (255, 255, 255))
        status_rect = status_text.get_rect(center=(self.width // 2, self.height - 50))
        self.screen.blit(status_text, status_rect)

        # For multiplayer, show waiting indicator when not your turn
        if game_mode != 'single' and not game.game_over and not your_turn:
            waiting_text = font_small.render("Waiting for opponent...", True, (255, 255, 0))
            waiting_rect = waiting_text.get_rect(center=(self.width // 2, self.height - 90))
            self.screen.blit(waiting_text, waiting_rect)

    def handle_click(self, pos):
        """Convert mouse click position to board index (0-8)"""
        # Only handle clicks within the board area (not the status area)
        if pos[1] < self.cell_size * 3:
            col = pos[0] // self.cell_size  # Which column (0,1,2)
            row = pos[1] // self.cell_size  # Which row (0,1,2)
            return row * 3 + col  # Convert 2D position to 1D index
        return None