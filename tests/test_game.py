import pytest
import os
import sys
import pygame
import importlib

SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

Game = importlib.import_module('Game').Game
GameState = importlib.import_module('game_state').GameState

@pytest.fixture(autouse=True)
def init_pygame():
    '''Inicjalizuje pygame w trybie 'dummy', aby nie otwierać okna.'''  
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.display.init()
    yield
    pygame.display.quit()

@pytest.fixture
def game(tmp_path, monkeypatch):
    '''Tworzy instancję Game z tymczasowym folderem photo_assets.'''  
    root = tmp_path / "project"
    assets = root / "assets" / "photo_assets"
    assets.mkdir(parents=True)
    (assets / "testwoj_01.png").write_text("dummy")
    g = Game()
    monkeypatch.setattr(g, 'image_folder', str(assets))
    return g

def test_sprawdz_odpowiedz_correct(game):
    '''Sprawdza, że poprawna odpowiedź zwraca True i zwiększa wynik.'''  
    filename = 'pomorskie_01.png'
    game.images = {filename: 'pomorskie'}
    game.score = 0
    result = game.sprawdz_odpowiedz(filename, 'pomorskie')
    assert result is True
    assert game.score == 1

def test_sprawdz_odpowiedz_incorrect(game):
    '''Sprawdza, że niepoprawna odpowiedź zwraca False i nie zmienia wyniku.'''  
    filename = 'lubelskie_foo.jpg'
    game.images = {filename: 'lubelskie'}
    game.score = 5
    result = game.sprawdz_odpowiedz(filename, 'mazowieckie')
    assert result is False
    assert game.score == 5

def test_sprawdz_odpowiedz_none_click(game):
    '''Sprawdza, że None zwraca False i nie zmienia wyniku.'''  
    filename = 'lubelskie_bar.jpg'
    game.images = {filename: 'lubelskie'}
    game.score = 2
    result = game.sprawdz_odpowiedz(filename, None)
    assert result is False
    assert game.score == 2

def test_load_images_folder_missing(monkeypatch):
    '''Sprawdza, że load_images zwraca 1, jak folder nie istnieje.'''  
    game = Game()
    monkeypatch.setattr(os.path, 'exists', lambda path: False)
    ret = game.load_images()
    assert ret == 1

def test_change_state(game):
    '''Sprawdza, że change_state poprawnie zmienia stan gry.'''  
    assert game.state == GameState.HOMEPAGE
    game.change_state(GameState.INSTRUCTIONPAGE)
    assert game.state == GameState.INSTRUCTIONPAGE

def test_pick_next_image_no_images(game):
    '''Sprawdza, że pick_next_image ustawia current_image na None, gdy brak obrazów.'''  
    game.image_keys = []
    game.pick_next_image()
    assert game.current_image is None
    assert game.current_image_surface is None

def test_pick_next_image_success(game, monkeypatch):
    '''Sprawdza poprawne wczytanie i skalowanie obrazu przez pick_next_image.'''  
    dummy_surface = pygame.Surface((100, 100))
    monkeypatch.setattr(pygame.image, 'load', lambda path: dummy_surface)
    game.image_keys = ['testwoj_01.png']
    game.pick_next_image()
    assert game.current_image == 'testwoj_01.png'
    assert isinstance(game.current_image_surface, pygame.Surface)

def test_draw_header_and_button_no_exceptions(game):
    '''Sprawdza, że draw_header i draw_button nie rzucają wyjątków.'''  
    game.screen = pygame.display.set_mode((800, 600))
    game.current_round = 1
    game.total_rounds = 3
    game.score = 2
    game.draw_header()
    rect = pygame.Rect(0, 0, 100, 50)
    game.draw_button('Test', rect, (0, 0, 0), (50, 50, 50), (10, 10))

def test_load_map_widget_missing(monkeypatch, game):
    '''Sprawdza, że load_map_widget zwraca None i cofa do HOMEPAGE, gdy brak pliku mapy.'''  
    monkeypatch.setattr(os.path, 'exists', lambda path: False)
    game.state = GameState.GAMEPAGE
    ret = game.load_map_widget()
    assert ret is None
    assert game.state == GameState.HOMEPAGE