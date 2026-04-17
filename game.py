import pygame


class TicTacToe:
    def __init__(self):
        self.board = [''] * 9
        self.current_player = 'X'
        self.winner = None
        self.game_over = False

    def make_move(self, position):
        if not self.game_over and self.board[position] == '':
            self.board[position] = self.current_player
            self.check_winner()
            if not self.game_over:
                self.switch_player()
            return True
        return False

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def check_winner(self):
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]

        for pattern in win_patterns:
            if (self.board[pattern[0]] and
                    self.board[pattern[0]] == self.board[pattern[1]] == self.board[pattern[2]]):
                self.winner = self.board[pattern[0]]
                self.game_over = True
                return

        if all(cell != '' for cell in self.board):
            self.game_over = True
            self.winner = 'Tie'

    def reset(self):
        self.board = [''] * 9
        self.current_player = 'X'
        self.winner = None
        self.game_over = False


class GameRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.width = 600
        self.height = 700
        self.cell_size = 200

    def draw_board(self, game, player_symbol, your_turn, game_mode='single'):
        self.screen.fill((30, 30, 30))

        # Draw grid
        for i in range(1, 3):
            pygame.draw.line(self.screen, (255, 255, 255),
                             (i * self.cell_size, 0),
                             (i * self.cell_size, self.height - 100), 3)
            pygame.draw.line(self.screen, (255, 255, 255),
                             (0, i * self.cell_size),
                             (self.width, i * self.cell_size), 3)

        # Draw X's and O's
        font = pygame.font.Font(None, 120)
        for i in range(9):
            if game.board[i]:
                x = (i % 3) * self.cell_size + self.cell_size // 2
                y = (i // 3) * self.cell_size + self.cell_size // 2
                color = (0, 255, 0) if game.board[i] == 'X' else (255, 100, 0)
                text = font.render(game.board[i], True, color)
                text_rect = text.get_rect(center=(x, y))
                self.screen.blit(text, text_rect)

        # Draw status text
        font_small = pygame.font.Font(None, 36)
        if game.game_over:
            if game.winner == 'Tie':
                status = "Game Over - Tie!"
            else:
                status = f"Game Over - Player {game.winner} wins!"
        else:
            if game_mode == 'single':
                if player_symbol == game.current_player:
                    status = f"Your turn ({player_symbol})"
                else:
                    status = "AI is thinking..."
            else:
                if your_turn:
                    status = f"Your turn ({player_symbol})"
                else:
                    status = f"Opponent's turn ({game.current_player})"

        status_text = font_small.render(status, True, (255, 255, 255))
        status_rect = status_text.get_rect(center=(self.width // 2, self.height - 50))
        self.screen.blit(status_text, status_rect)

        # Draw turn indicator for multiplayer
        if game_mode != 'single' and not game.game_over and not your_turn:
            waiting_text = font_small.render("Waiting for opponent...", True, (255, 255, 0))
            waiting_rect = waiting_text.get_rect(center=(self.width // 2, self.height - 90))
            self.screen.blit(waiting_text, waiting_rect)

    def handle_click(self, pos):
        if pos[1] < self.cell_size * 3:
            col = pos[0] // self.cell_size
            row = pos[1] // self.cell_size
            return row * 3 + col
        return None