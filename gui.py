import pygame
import sys
from PIL import Image
import os
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 160, 0)

FONT = pygame.font.SysFont('Arial', 32)
SMALL_FONT = pygame.font.SysFont('Arial', 24)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Znajdź Województwo")
        self.clock = pygame.time.Clock()
        self.state = "start"
        self.player_name = ""
        self.input_text = ""
        self.current_round = 0
        self.total_rounds = 3
        self.images = ["foto1.jpg", "foto2.jpg", "foto3.jpg"]
        self.running = True
        self.score = 0
        self.map_image = self.load_image("mapa_polski.jpg", (400, 400))


    def load_image(self, path, size=None):
        if not os.path.exists(path):
            img = Image.new("RGB", (300, 300), color="gray")
        else:
            img = Image.open(path)
        if size:
            img = img.resize(size)
        return pygame.image.fromstring(img.tobytes(), img.size, img.mode)

    def draw_button(self, rect, text, color=GREEN, hover_color=DARK_GREEN):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = pygame.Rect(rect).collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, hover_color if is_hover else color, rect, border_radius=10)
        label = FONT.render(text, True, WHITE)
        label_rect = label.get_rect(center=(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2))
        self.screen.blit(label, label_rect)
        return is_hover and pygame.mouse.get_pressed()[0]

    def draw_close_button(self):
        close_rect = pygame.Rect(SCREEN_WIDTH - 50, 10, 40, 40)
        pygame.draw.rect(self.screen, (200, 0, 0), close_rect)
        x_label = FONT.render("X", True, WHITE)
        self.screen.blit(x_label, (SCREEN_WIDTH - 40, 10))
        return close_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]

    def draw_text_center(self, text, y, font=FONT):
        rendered = font.render(text, True, BLACK)
        rect = rendered.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.screen.blit(rendered, rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == "name":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.player_name = self.input_text.strip()
                        self.input_text = ""
                        if self.player_name:
                            self.state = "game"
                            self.current_round = 0
                            self.score = 0
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        self.input_text += event.unicode

            elif self.state == "game":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.next_round()

    def next_round(self):
        self.current_round += 1
        if self.current_round >= self.total_rounds:
            self.state = "end"

    def run(self):
        while self.running:
            self.handle_events()

            self.screen.fill(WHITE)
            if self.draw_close_button():
                self.running = False

            if self.state == "start":
                self.draw_text_center("Witaj w grze: Znajdź Województwo", 200)
                if self.draw_button((SCREEN_WIDTH // 2 - 100, 300, 200, 60), "GRAJ"):
                    self.state = "name"

            elif self.state == "name":
                self.draw_text_center("Wpisz swoje imię:", 200)
                input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 260, 300, 50)
                pygame.draw.rect(self.screen, (230, 230, 230), input_box, border_radius=8)
                name_surface = FONT.render(self.input_text, True, BLACK)
                self.screen.blit(name_surface, (input_box.x + 10, input_box.y + 10))

            elif self.state == "game":
                self.draw_text_center(f"Runda {self.current_round + 1} z {self.total_rounds}", 30, SMALL_FONT)

                if self.current_round < len(self.images):
                    photo = self.load_image(self.images[self.current_round], (300, 300))
                    self.screen.blit(photo, (50, 150))

                self.screen.blit(self.map_image, (550, 150))
                self.draw_text_center("Naciśnij ENTER, aby przejść dalej", 600, SMALL_FONT)

            elif self.state == "end":
                self.draw_text_center(f"Dziękujemy za grę, {self.player_name}!", 180)
                self.draw_text_center(f"Wynik: {self.score} / {self.total_rounds}", 240, SMALL_FONT)

                if self.draw_button((SCREEN_WIDTH // 2 - 150, 300, 300, 60), "Zagraj jeszcze raz"):
                    self.state = "game"
                    self.current_round = 0
                    self.score = 0

                if self.draw_button((SCREEN_WIDTH // 2 - 150, 400, 300, 60), "Powrót do menu"):
                    self.state = "start"

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
