import pygame
import sys
from network import NetworkHandler
from game import GameRenderer, TicTacToe


class MultiplayerGame:
    """Client for multiplayer Tic-Tac-Toe"""

    def __init__(self):
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((600, 700))
        pygame.display.set_caption("Multiplayer Tic-Tac-Toe")
        self.clock = pygame.time.Clock()

        # Network handler for server communication
        self.network = NetworkHandler()
        # Visual renderer
        self.renderer = GameRenderer(self.screen)
        # Local game state (kept in sync with server)
        self.game = TicTacToe()

        # Player-specific data
        self.player_symbol = None  # 'X' or 'O' from server
        self.your_turn = False  # Is it this player's turn?
        self.game_started = False  # Has the game started?

    def connect_screen(self):
        """Display connection screen to get server address from user"""
        font = pygame.font.Font(None, 48)
        input_box = pygame.Rect(200, 300, 200, 50)
        active = False
        text = 'localhost'  # Default server address
        error_msg = ""

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Activate input box when clicked
                    active = input_box.collidepoint(event.pos)
                if event.type == pygame.KEYDOWN and active:
                    if event.key == pygame.K_RETURN:
                        # Try to connect to server
                        if self.network.connect_to_server(text, 5555):
                            self.player_symbol = self.network.player_symbol
                            # Register callback for game state updates
                            self.network.add_callback(self.update_game_state)
                            return True
                        else:
                            error_msg = "Cannot connect to server!"
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]  # Remove last character
                    else:
                        text += event.unicode  # Add typed character

            # Draw connection screen
            self.screen.fill((30, 30, 30))

            title = font.render("Multiplayer Tic-Tac-Toe", True, (255, 255, 255))
            title_rect = title.get_rect(center=(300, 150))
            self.screen.blit(title, title_rect)

            subtitle = pygame.font.Font(None, 36).render("Server Address:", True, (200, 200, 200))
            sub_rect = subtitle.get_rect(center=(300, 250))
            self.screen.blit(subtitle, sub_rect)

            # Draw input box
            txt_surface = font.render(text, True, (255, 255, 255))
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            self.screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(self.screen, (255, 255, 255), input_box, 2)

            # Show error message if connection failed
            if error_msg:
                error = pygame.font.Font(None, 24).render(error_msg, True, (255, 0, 0))
                error_rect = error.get_rect(center=(300, 400))
                self.screen.blit(error, error_rect)

            pygame.display.flip()
            self.clock.tick(30)

    def update_game_state(self, game_state):
        """Called when server sends updated game state"""
        # Update local game with server data
        self.game.board = game_state['board']
        self.game.current_player = game_state['current_player']
        self.game.winner = game_state['winner']
        self.game.game_over = game_state['game_over']
        self.your_turn = game_state['your_turn']
        self.game_started = game_state['game_started']

        # Debug output
        print(f"Update - Your symbol: {self.player_symbol}, Your turn: {self.your_turn}")

    def run(self):
        """Main game loop"""
        # First, connect to server
        if not self.connect_screen():
            pygame.quit()
            sys.exit()

        running = True

        # WAITING SCREEN - Show while waiting for opponent
        waiting = True
        while running and waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # Check if game has started (both players connected)
            if self.game_started:
                waiting = False
                break

            # Draw waiting screen
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

        # MAIN GAME LOOP - Game is active
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Only process clicks if it's your turn and game not over
                    if self.your_turn and not self.game.game_over:
                        pos = pygame.mouse.get_pos()
                        position = self.renderer.handle_click(pos)
                        # Valid click and empty cell?
                        if position is not None and self.game.board[position] == '':
                            print(f"Sending move to {position}")
                            self.network.send_move(position)

            # Draw current game state
            self.renderer.draw_board(self.game, self.player_symbol, self.your_turn, 'multi')

            # Draw instructions
            font_small = pygame.font.Font(None, 24)
            info = font_small.render("Press ESC to quit", True, (200, 200, 200))
            self.screen.blit(info, (20, 660))

            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS

        # Clean up
        self.network.disconnect()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = MultiplayerGame()
    game.run()