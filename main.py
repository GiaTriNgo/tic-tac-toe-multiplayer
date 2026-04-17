import pygame
import sys
import random
from game import TicTacToe, GameRenderer


# AI Player class for single player
class AIPlayer:
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty

    def get_move(self, board, ai_symbol):
        if self.difficulty == 'easy':
            return self.get_random_move(board)
        elif self.difficulty == 'medium':
            return self.get_medium_move(board, ai_symbol)
        else:
            return self.get_best_move(board, ai_symbol)

    def get_random_move(self, board):
        empty_cells = [i for i, cell in enumerate(board) if cell == '']
        return random.choice(empty_cells) if empty_cells else None

    def get_medium_move(self, board, ai_symbol):
        if random.random() < 0.6:
            return self.get_best_move(board, ai_symbol)
        else:
            return self.get_random_move(board)

    def get_best_move(self, board, ai_symbol):
        opponent = 'O' if ai_symbol == 'X' else 'X'
        best_score = float('-inf')
        best_move = None

        for i in range(9):
            if board[i] == '':
                board[i] = ai_symbol
                score = self.minimax(board, 0, False, ai_symbol, opponent)
                board[i] = ''
                if score > best_score:
                    best_score = score
                    best_move = i
        return best_move if best_move is not None else self.get_random_move(board)

    def minimax(self, board, depth, is_maximizing, ai_symbol, opponent_symbol):
        winner = self.check_winner(board)
        if winner == ai_symbol:
            return 10 - depth
        elif winner == opponent_symbol:
            return depth - 10
        elif all(cell != '' for cell in board):
            return 0

        if is_maximizing:
            best_score = float('-inf')
            for i in range(9):
                if board[i] == '':
                    board[i] = ai_symbol
                    score = self.minimax(board, depth + 1, False, ai_symbol, opponent_symbol)
                    board[i] = ''
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(9):
                if board[i] == '':
                    board[i] = opponent_symbol
                    score = self.minimax(board, depth + 1, True, ai_symbol, opponent_symbol)
                    board[i] = ''
                    best_score = min(score, best_score)
            return best_score

    def check_winner(self, board):
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for pattern in win_patterns:
            if (board[pattern[0]] and
                    board[pattern[0]] == board[pattern[1]] == board[pattern[2]]):
                return board[pattern[0]]
        return None


class SinglePlayerGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 700))
        pygame.display.set_caption("Tic-Tac-Toe - Single Player")
        self.clock = pygame.time.Clock()
        self.game = TicTacToe()
        self.renderer = GameRenderer(self.screen)
        self.ai = None
        self.player_symbol = 'X'
        self.ai_symbol = 'O'
        self.is_player_turn = True
        self.ai_thinking = False
        self.ai_move_timer = 0

    def show_menu(self):
        font_title = pygame.font.Font(None, 72)
        font_button = pygame.font.Font(None, 48)

        easy_btn = pygame.Rect(200, 250, 200, 60)
        medium_btn = pygame.Rect(200, 330, 200, 60)
        hard_btn = pygame.Rect(200, 410, 200, 60)
        back_btn = pygame.Rect(200, 510, 200, 60)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
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
                        return False

            self.screen.fill((30, 30, 30))
            title = font_title.render("Select Difficulty", True, (255, 255, 255))
            title_rect = title.get_rect(center=(300, 100))
            self.screen.blit(title, title_rect)

            buttons = [(easy_btn, "Easy", (0, 150, 0)),
                       (medium_btn, "Medium", (0, 150, 200)),
                       (hard_btn, "Hard", (200, 50, 50)),
                       (back_btn, "Back", (100, 100, 100))]

            for btn, text, color in buttons:
                pygame.draw.rect(self.screen, color, btn)
                text_surface = font_button.render(text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=btn.center)
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            self.clock.tick(30)

    def reset_game(self):
        self.game.reset()
        if random.choice([True, False]):
            self.player_symbol = 'X'
            self.ai_symbol = 'O'
            self.is_player_turn = True
        else:
            self.player_symbol = 'O'
            self.ai_symbol = 'X'
            self.is_player_turn = False
            self.ai_thinking = True
            self.ai_move_timer = pygame.time.get_ticks() + 500

    def run(self):
        if not self.show_menu():
            return False

        self.reset_game()
        running = True

        while running:
            current_time = pygame.time.get_ticks()

            if not self.is_player_turn and not self.game.game_over and not self.ai_thinking:
                self.ai_thinking = True
                self.ai_move_timer = current_time + 500

            if self.ai_thinking and current_time >= self.ai_move_timer:
                move = self.ai.get_move(self.game.board, self.ai_symbol)
                if move is not None:
                    self.game.make_move(move)
                    self.is_player_turn = True
                self.ai_thinking = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game.game_over:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        return True
                    elif event.key == pygame.K_n:
                        self.reset_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.is_player_turn and not self.game.game_over:
                        pos = pygame.mouse.get_pos()
                        position = self.renderer.handle_click(pos)
                        if position is not None and self.game.board[position] == '':
                            self.game.make_move(position)
                            self.is_player_turn = False

            self.renderer.draw_board(self.game, self.player_symbol, self.is_player_turn, 'single')

            font_small = pygame.font.Font(None, 24)
            if self.game.game_over:
                reset_text = font_small.render("Press R for new game | ESC for menu",
                                               True, (200, 200, 200))
            else:
                reset_text = font_small.render("Press ESC for menu", True, (200, 200, 200))
            self.screen.blit(reset_text, (20, 660))

            pygame.display.flip()
            self.clock.tick(60)

        return False


class MainMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 700))
        pygame.display.set_caption("Tic-Tac-Toe")
        self.clock = pygame.time.Clock()

    def run(self):
        font_title = pygame.font.Font(None, 72)
        font_button = pygame.font.Font(None, 48)

        single_btn = pygame.Rect(200, 250, 200, 60)
        multi_btn = pygame.Rect(200, 350, 200, 60)
        quit_btn = pygame.Rect(200, 450, 200, 60)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if single_btn.collidepoint(event.pos):
                        single_player = SinglePlayerGame()
                        if not single_player.run():
                            return
                    elif multi_btn.collidepoint(event.pos):
                        # Import here to avoid circular imports
                        from multiplayer_client import MultiplayerGame
                        multi_player = MultiplayerGame()
                        multi_player.run()
                    elif quit_btn.collidepoint(event.pos):
                        return

            self.screen.fill((30, 30, 30))
            title = font_title.render("Tic-Tac-Toe", True, (255, 255, 255))
            title_rect = title.get_rect(center=(300, 100))
            self.screen.blit(title, title_rect)

            buttons = [(single_btn, "Single Player", (0, 100, 200)),
                       (quit_btn, "Quit", (100, 100, 100))]

            for btn, text, color in buttons:
                pygame.draw.rect(self.screen, color, btn)
                text_surface = font_button.render(text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=btn.center)
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            self.clock.tick(30)


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
    pygame.quit()
    sys.exit()