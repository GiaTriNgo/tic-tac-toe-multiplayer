import pygame
import sys
import random
from game import TicTacToe, GameRenderer


# ============================================================================
# AI PLAYER CLASS - Controls the computer opponent
# ============================================================================

class AIPlayer:
    """Artificial Intelligence for single-player mode"""

    def __init__(self, difficulty='medium'):
        # Difficulty levels: 'easy', 'medium', 'hard'
        self.difficulty = difficulty

    def get_move(self, board, ai_symbol):
        """Returns the best move based on selected difficulty"""
        if self.difficulty == 'easy':
            # Easy: completely random moves
            return self.get_random_move(board)
        elif self.difficulty == 'medium':
            # Medium: 60% optimal, 40% random
            return self.get_medium_move(board, ai_symbol)
        else:
            # Hard: always optimal (unbeatable)
            return self.get_best_move(board, ai_symbol)

    def get_random_move(self, board):
        """Choose a random empty cell"""
        # Find all empty cells (where board[i] == '')
        empty_cells = [i for i, cell in enumerate(board) if cell == '']
        # Return random choice or None if board is full
        return random.choice(empty_cells) if empty_cells else None

    def get_medium_move(self, board, ai_symbol):
        """Mix of random and optimal moves"""
        # 60% chance of using optimal move, 40% chance of random
        if random.random() < 0.6:
            return self.get_best_move(board, ai_symbol)
        else:
            return self.get_random_move(board)

    def get_best_move(self, board, ai_symbol):
        """Find the best possible move using minimax algorithm"""
        # Determine opponent's symbol
        opponent = 'O' if ai_symbol == 'X' else 'X'
        best_score = float('-inf')  # Start with worst possible score
        best_move = None

        # Try every possible move
        for i in range(9):
            if board[i] == '':  # Only consider empty cells
                # Simulate making this move
                board[i] = ai_symbol
                # Calculate score for this move
                score = self.minimax(board, 0, False, ai_symbol, opponent)
                # Undo the move
                board[i] = ''

                # If this move is better than previous best, remember it
                if score > best_score:
                    best_score = score
                    best_move = i

        # Fallback to random move if no best move found
        return best_move if best_move is not None else self.get_random_move(board)

    def minimax(self, board, depth, is_maximizing, ai_symbol, opponent_symbol):
        """
        Minimax algorithm for perfect AI play.
        Recursively evaluates all possible future moves.

        depth: How many moves ahead we're looking
        is_maximizing: True for AI's turn, False for opponent's turn
        """
        # Check if game ended (base case)
        winner = self.check_winner(board)
        if winner == ai_symbol:
            return 10 - depth  # AI wins (positive score)
        elif winner == opponent_symbol:
            return depth - 10  # Opponent wins (negative score)
        elif all(cell != '' for cell in board):
            return 0  # Tie game

        if is_maximizing:
            # AI's turn - try to maximize score
            best_score = float('-inf')
            for i in range(9):
                if board[i] == '':
                    board[i] = ai_symbol
                    score = self.minimax(board, depth + 1, False, ai_symbol, opponent_symbol)
                    board[i] = ''
                    best_score = max(score, best_score)
            return best_score
        else:
            # Opponent's turn - try to minimize score (they want AI to lose)
            best_score = float('inf')
            for i in range(9):
                if board[i] == '':
                    board[i] = opponent_symbol
                    score = self.minimax(board, depth + 1, True, ai_symbol, opponent_symbol)
                    board[i] = ''
                    best_score = min(score, best_score)
            return best_score

    def check_winner(self, board):
        """Check if there's a winner on the given board state"""
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]  # Diagonals
        ]
        for pattern in win_patterns:
            if (board[pattern[0]] and
                    board[pattern[0]] == board[pattern[1]] == board[pattern[2]]):
                return board[pattern[0]]  # Return 'X' or 'O'
        return None  # No winner yet


# ============================================================================
# SINGLE PLAYER GAME CLASS - Manages player vs AI gameplay
# ============================================================================

class SinglePlayerGame:
    """Handles single-player mode with AI opponent"""

    def __init__(self):
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((600, 700))
        pygame.display.set_caption("Tic-Tac-Toe - Single Player")
        self.clock = pygame.time.Clock()

        # Game components
        self.game = TicTacToe()  # Game logic
        self.renderer = GameRenderer(self.screen)  # Visual renderer
        self.ai = None  # AI player (set after difficulty selection)

        # Player and AI symbols
        self.player_symbol = 'X'  # Player's symbol
        self.ai_symbol = 'O'  # AI's symbol
        self.is_player_turn = True  # True = player, False = AI

        # AI thinking timer (creates delay for better UX)
        self.ai_thinking = False
        self.ai_move_timer = 0

    def show_menu(self):
        """Display difficulty selection menu"""
        font_title = pygame.font.Font(None, 72)
        font_button = pygame.font.Font(None, 48)

        # Create button rectangles (x, y, width, height)
        easy_btn = pygame.Rect(200, 250, 200, 60)
        medium_btn = pygame.Rect(200, 330, 200, 60)
        hard_btn = pygame.Rect(200, 410, 200, 60)
        back_btn = pygame.Rect(200, 510, 200, 60)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False  # User closed window
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check which button was clicked
                    if easy_btn.collidepoint(event.pos):
                        self.ai = AIPlayer('easy')
                        return True
                    elif medium_btn.collidepoint(event.pos):
                        self.ai = AIPlayer('medium')
                        return True
                    elif hard_btn.collidepoint(event.pos):
                        self.ai = AIPlayer('hard')
                        return True
                    elif back_btn.collidepoint(event.pos):
                        return False  # Go back to main menu

            # Draw the menu
            self.screen.fill((30, 30, 30))
            title = font_title.render("Select Difficulty", True, (255, 255, 255))
            title_rect = title.get_rect(center=(300, 100))
            self.screen.blit(title, title_rect)

            # List of buttons with their properties
            buttons = [(easy_btn, "Easy", (0, 150, 0)),  # Green
                       (medium_btn, "Medium", (0, 150, 200)),  # Blue
                       (hard_btn, "Hard", (200, 50, 50)),  # Red
                       (back_btn, "Back", (100, 100, 100))]  # Gray

            # Draw each button
            for btn, text, color in buttons:
                pygame.draw.rect(self.screen, color, btn)
                text_surface = font_button.render(text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=btn.center)
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            self.clock.tick(30)

    def reset_game(self):
        """Reset the game for a new round"""
        self.game.reset()

        # Randomly decide who goes first (50% chance each)
        if random.choice([True, False]):
            # Player goes first
            self.player_symbol = 'X'
            self.ai_symbol = 'O'
            self.is_player_turn = True
        else:
            # AI goes first
            self.player_symbol = 'O'
            self.ai_symbol = 'X'
            self.is_player_turn = False
            self.ai_thinking = True
            # AI will move after 500ms delay
            self.ai_move_timer = pygame.time.get_ticks() + 500

    def run(self):
        """Main game loop for single-player mode"""
        # Show difficulty menu first
        if not self.show_menu():
            return False  # User went back or quit

        self.reset_game()
        running = True

        while running:
            current_time = pygame.time.get_ticks()

            # ===== AI TURN HANDLING =====
            # Check if it's AI's turn and game is active
            if not self.is_player_turn and not self.game.game_over and not self.ai_thinking:
                self.ai_thinking = True
                self.ai_move_timer = current_time + 500  # 0.5 second delay

            # Execute AI move after delay
            if self.ai_thinking and current_time >= self.ai_move_timer:
                move = self.ai.get_move(self.game.board, self.ai_symbol)
                if move is not None:
                    self.game.make_move(move)
                    self.is_player_turn = True  # Switch to player's turn
                self.ai_thinking = False

            # ===== EVENT HANDLING =====
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game.game_over:
                        # R key: Restart game with same difficulty
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        # ESC key: Return to main menu
                        return True
                    elif event.key == pygame.K_n:
                        # N key: New game (reset without changing difficulty)
                        self.reset_game()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Handle player move
                    if self.is_player_turn and not self.game.game_over:
                        pos = pygame.mouse.get_pos()
                        position = self.renderer.handle_click(pos)
                        # Valid move? (position not None and cell empty)
                        if position is not None and self.game.board[position] == '':
                            self.game.make_move(position)
                            self.is_player_turn = False  # Switch to AI's turn

            # ===== DRAW EVERYTHING =====
            self.renderer.draw_board(self.game, self.player_symbol, self.is_player_turn, 'single')

            # Draw control hints at bottom of screen
            font_small = pygame.font.Font(None, 24)
            if self.game.game_over:
                reset_text = font_small.render("Press R for new game | ESC for menu",
                                               True, (200, 200, 200))
            else:
                reset_text = font_small.render("Press ESC for menu", True, (200, 200, 200))
            self.screen.blit(reset_text, (20, 660))

            pygame.display.flip()
            self.clock.tick(60)  # 60 frames per second

        return False


# ============================================================================
# MAIN MENU CLASS - Entry point for the game
# ============================================================================

class MainMenu:
    """Main menu for selecting game mode"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 700))
        pygame.display.set_caption("Tic-Tac-Toe")
        self.clock = pygame.time.Clock()

    def run(self):
        """Display main menu and handle mode selection"""
        font_title = pygame.font.Font(None, 72)
        font_button = pygame.font.Font(None, 48)

        # Create button rectangles
        single_btn = pygame.Rect(200, 250, 200, 60)
        multi_btn = pygame.Rect(200, 350, 200, 60)
        quit_btn = pygame.Rect(200, 450, 200, 60)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return  # Exit the game

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if single_btn.collidepoint(event.pos):
                        # Start single-player mode
                        single_player = SinglePlayerGame()
                        if not single_player.run():
                            return  # User quit from single-player menu

                    elif multi_btn.collidepoint(event.pos):
                        # Start multiplayer mode
                        # Import here to avoid circular import issues
                        from multiplayer_client import MultiplayerGame
                        multi_player = MultiplayerGame()
                        multi_player.run()

                    elif quit_btn.collidepoint(event.pos):
                        return  # Exit game

            # Draw main menu
            self.screen.fill((30, 30, 30))

            # Draw title
            title = font_title.render("Tic-Tac-Toe", True, (255, 255, 255))
            title_rect = title.get_rect(center=(300, 100))
            self.screen.blit(title, title_rect)

            # Draw buttons (multiplayer button is commented out in your version)
            buttons = [(single_btn, "Single Player", (0, 100, 200)),
                       (quit_btn, "Quit", (100, 100, 100))]

            for btn, text, color in buttons:
                pygame.draw.rect(self.screen, color, btn)
                text_surface = font_button.render(text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=btn.center)
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            self.clock.tick(30)


# ============================================================================
# GAME ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Create and run the main menu
    menu = MainMenu()
    menu.run()
    # Clean up Pygame when exiting
    pygame.quit()
    sys.exit()