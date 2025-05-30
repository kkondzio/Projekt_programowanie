"""Moduł gry 'Znajdź Województwo' z wykorzystaniem biblioteki Pygame."""

import sys
import pygame
from game_state import GameState

# Inicjalizacja Pygame
pygame.init()

# Stałe
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 160, 0)

# Czcionki
FONT = pygame.font.SysFont('Arial', 32)
SMALL_FONT = pygame.font.SysFont('Arial', 24)


class Game: # TODO: wygląd stron i rozgrywka
    """Główna klasa gry."""

    def __init__(self):
        """Inicjalizuje atrybuty gry i stan początkowy."""
        self.state = GameState.HOMEPAGE
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Znajdź Województwo")
        self.player_name = ""
        self.input_text = ""
        self.current_round = 0
        self.total_rounds = 3
        self.images = dict()  # TODO: słownik zdjęcie - województwo Maks
        self.running = True
        self.score = 0
        self.kolory_wojewodztw = {
            (103, 186, 144): "dolnośląskie",
            (140, 96, 59): "kujawsko-pomorskie",
            (235, 88, 72): "lubelskie",
            (90, 192, 196): "lubuskie",
            (199, 157, 109): "łódzkie",
            (252, 225, 74): "małopolskie",
            (238, 114, 124): "mazowieckie",
            (89, 174, 83): "opolskie",
            (251, 196, 51): "podkarpackie",
            (204, 133, 175): "podlaskie",
            (103, 107, 170): "pomorskie",
            (178, 205, 74): "śląskie",
            (243, 149, 79): "świętokrzyskie",
            (190, 104, 151): "warmińsko-mazurskie",
            (166, 123, 81): "wielkopolskie",
            (87, 133, 195): "zachodniopomorskie"
        }

    def run(self):
        """Główna pętla gry obsługująca przechodzenie między stanami."""
        clock = pygame.time.Clock()
        while self.state != GameState.END:
            if self.state == GameState.HOMEPAGE:
                self.handle_homepage()
            elif self.state == GameState.STARTPAGE:
                self.handle_startpage()
            elif self.state == GameState.GAMEPAGE:
                self.handle_gamepage()
            elif self.state == GameState.RESULTPAGE:
                self.handle_resultpage()
            clock.tick(60)
        pygame.quit()
        sys.exit()

    def draw_button(self, text, rect, color, hover_color, mouse_pos): 
        """Rysuje przycisk z tekstem i obsługuje efekt najechania."""
        button_color = hover_color if rect.collidepoint(mouse_pos) else color
        pygame.draw.rect(self.screen, button_color, rect)
        text_surface = FONT.render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def handle_homepage(self):
        """Obsługuje ekran startowy z przyciskiem Start i Zakończ."""
        while self.state == GameState.HOMEPAGE:
            self.screen.fill(WHITE)
            mouse_pos = pygame.mouse.get_pos()

            # Przyciski
            start_btn = pygame.Rect(490, 250, 300, 70)
            exit_btn = pygame.Rect(490, 350, 300, 70)

            self.draw_button("Start Gry", start_btn, GREEN, DARK_GREEN, mouse_pos)
            self.draw_button("Zakończ", exit_btn, GREEN, DARK_GREEN, mouse_pos)

            # Zdarzenia
            for event in pygame.event.get(): # TODO: cała obsługa zdarzeń
                if event.type == pygame.QUIT:
                    self.change_state(GameState.END)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if start_btn.collidepoint(event.pos):
                        self.change_state(GameState.STARTPAGE)
                        return
                    elif exit_btn.collidepoint(event.pos):
                        self.change_state(GameState.END)
                        return

            pygame.display.flip()

    def handle_startpage(self): 
        """Obsługuje stronę rozpoczęcia rozgrywki."""
        self.screen.fill(WHITE)
        text = FONT.render("Tu będzie start właściwej gry", True, BLACK)
        self.screen.blit(text, (400, 300))
        pygame.display.flip()
        pygame.time.wait(2000)
        self.change_state(GameState.GAMEPAGE)

    def handle_gamepage(self):
        """Obsługuje stronę gry (rozgrywkę)."""
        self.screen.fill(WHITE)
        text = FONT.render("Tu będzie rozgrywka", True, BLACK)
        self.screen.blit(text, (500, 300))
        pygame.display.flip()
        pygame.time.wait(2000)
        self.change_state(GameState.RESULTPAGE)

    def handle_resultpage(self):
        """Wyświetla wynik końcowy i wraca do strony startowej."""
        self.screen.fill(WHITE)
        text = FONT.render(f"Wynik końcowy: {self.score}", True, BLACK)
        self.screen.blit(text, (500, 300))
        pygame.display.flip()
        pygame.time.wait(3000)
        self.change_state(GameState.HOMEPAGE)

    def change_state(self, new_state: GameState):
        """Zmienia stan gry na nowy."""
        self.state = new_state
        print('Zmieniono stan')