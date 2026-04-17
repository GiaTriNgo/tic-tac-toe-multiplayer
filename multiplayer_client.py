import pygame
import sys
from network import NetworkHandler
from game import GameRenderer, TicTacToe


class MultiplayerGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 700))
        pygame.display.set_caption("Multiplayer Tic-Tac-Toe")
        self.clock = pygame.time.Clock()

        self.network = NetworkHandler()
        self.renderer = GameRenderer(self.screen)
        self.game = TicTacToe()
        self.player_symbol = None
        self.your_turn = False
        self.game_started = False

    def connect_screen(self):
        font = pygame.font.Font(None, 48)
        input_box = pygame.Rect(200, 300, 200, 50)
        active = False
        text = 'localhost'
        error_msg = ""

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    active = input_box.collidepoint(event.pos)
                if event.type == pygame.KEYDOWN and active:
                    if event.key == pygame.K_RETURN:
                        if self.network.connect_to_server(text, 5555):
                            self.player_symbol = self.network.player_symbol
                            self.network.add_callback(self.update_game_state)
                            return True
                        else:
                            error_msg = "Cannot connect to server!"
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

            self.screen.fill((30, 30, 30))

            title = font.render("Multiplayer Tic-Tac-Toe", True, (255, 255, 255))
            title_rect = title.get_rect(center=(300, 150))
            self.screen.blit(title, title_rect)

            subtitle = pygame.font.Font(None, 36).render("Server Address:", True, (200, 200, 200))
            sub_rect = subtitle.get_rect(center=(300, 250))
            self.screen.blit(subtitle, sub_rect)

            txt_surface = font.render(text, True, (255, 255, 255))
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            self.screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(self.screen, (255, 255, 255), input_box, 2)

            if error_msg:
                error = pygame.font.Font(None, 24).render(error_msg, True, (255, 0, 0))
                error_rect = error.get_rect(center=(300, 400))
                self.screen.blit(error, error_rect)

            pygame.display.flip()
            self.clock.tick(30)

    def update_game_state(self, game_state):
        """Update local game from server data"""
        self.game.board = game_state['board']
        self.game.current_player = game_state['current_player']
        self.game.winner = game_state['winner']
        self.game.game_over = game_state['game_over']
        self.your_turn = game_state['your_turn']
        self.game_started = game_state['game_started']

        # Debug print
        print(f"Update - Your symbol: {self.player_symbol}, Your turn: {self.your_turn}")

    def run(self):
        if not self.connect_screen():
            pygame.quit()
            sys.exit()

        running = True

        # Waiting screen
        waiting = True
        while running and waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            if self.game_started:
                waiting = False
                break

            self.screen.fill((30, 30, 30))
            font = pygame.font.Font(None, 48)

            player_text = font.render(f"You are Player {self.player_symbol}", True, (255, 255, 0))
            self.screen.blit(player_text, player_text.get_rect(center=(300, 200)))

            waiting_text = font.render("Waiting for opponent...", True, (255, 255, 255))
            self.screen.blit(waiting_text, waiting_text.get_rect(center=(300, 300)))

            esc_text = pygame.font.Font(None, 24).render("Press ESC to quit", True, (200, 200, 200))
            self.screen.blit(esc_text, (20, 660))

            pygame.display.flip()
            self.clock.tick(30)

        # Main game loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.your_turn and not self.game.game_over:
                        pos = pygame.mouse.get_pos()
                        position = self.renderer.handle_click(pos)
                        if position is not None and self.game.board[position] == '':
                            print(f"Sending move to {position}")
                            self.network.send_move(position)

            self.renderer.draw_board(self.game, self.player_symbol, self.your_turn, 'multi')

            # Instructions
            font_small = pygame.font.Font(None, 24)
            info = font_small.render("Press ESC to quit", True, (200, 200, 200))
            self.screen.blit(info, (20, 660))

            pygame.display.flip()
            self.clock.tick(60)

        self.network.disconnect()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = MultiplayerGame()
    game.run()