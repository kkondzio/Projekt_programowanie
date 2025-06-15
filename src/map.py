import pygame
import shapefile
from shapely.geometry import Polygon, Point
from shapely.prepared import prep
from typing import List, Optional, Tuple, Dict, Any

class PolandMapWidget:
    """Widget wyświetlający interaktywną mapę Polski na podstawie pliku .shp."""

    def __init__(self, x: int, y: int, width: int, height: int, shapefile_path: str) -> None:
        """Inicjalizuje widget mapy Polski i ładuje dane z `.shp`."""
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.visible: bool = True
        self.active: bool = True

        self.hovered_voivodeship: Optional[Dict[str, Any]] = None
        self.selected_voivodeship: Optional[Dict[str, Any]] = None
        self.last_mouse_pos: Optional[Tuple[int, int]] = None
        self.cache_surface: Optional[pygame.Surface] = None
        self.needs_redraw: bool = True

        self.voivodeships: List[Dict[str, Any]] = []
        self.colors: List[Tuple[int, int, int, int]] = []
        self.min_x = self.max_x = self.min_y = self.max_y = 0.0

        self.load_shapefile(shapefile_path)

    def load_shapefile(self, path: str) -> None:
        """Ładuje dane mapy z pliku shapefile."""
        sf = shapefile.Reader(path)
        shapes = sf.shapes()
        records = sf.records()

        if not shapes:
            return

        self.min_x, self.max_x = shapes[0].bbox[0], shapes[0].bbox[2]
        self.min_y, self.max_y = shapes[0].bbox[1], shapes[0].bbox[3]
        for shape in shapes:
            self.min_x = min(self.min_x, shape.bbox[0])
            self.max_x = max(self.max_x, shape.bbox[2])
            self.min_y = min(self.min_y, shape.bbox[1])
            self.max_y = max(self.max_y, shape.bbox[3])

        self.colors = [
            (255, 0, 0, 150), (0, 255, 0, 150), (0, 0, 255, 150),
            (255, 255, 0, 150), (255, 0, 255, 150), (0, 255, 255, 150),
            (128, 0, 0, 150), (0, 128, 0, 150), (0, 0, 128, 150),
            (128, 128, 0, 150), (128, 0, 128, 150), (0, 128, 128, 150),
            (192, 192, 192, 150), (128, 128, 128, 150),
            (153, 153, 255, 150), (153, 51, 102, 150),
        ]

        for i, (shape, record) in enumerate(zip(shapes, records)):
            name = record[4] if len(record) > 4 else f"Województwo {i+1}"
            polygons = []
            prepared_polygons = []
            parts = list(shape.parts) + [len(shape.points)]
            for j in range(len(parts) - 1):
                pts = shape.points[parts[j]:parts[j+1]]
                poly = Polygon(pts)
                polygons.append(poly)
                prepared_polygons.append(prep(poly))
            color = self.colors[i % len(self.colors)]
            hover_color = tuple(
                min(255, c + 50) if idx < 3 else c for idx, c in enumerate(color)
            )
            self.voivodeships.append({
                'name': name,
                'polygons': polygons,
                'prepared_polygons': prepared_polygons,
                'color': color,
                'hover_color': hover_color,
            })

    def update(self) -> None:
        """Aktualizuje stan mapy (obsługa efektu najechania myszą)."""
        if not (self.active and self.visible):
            self.hovered_voivodeship = None
            return

        mouse = pygame.mouse.get_pos()
        if mouse == self.last_mouse_pos:
            return
        self.last_mouse_pos = mouse

        if not self.rect.collidepoint(mouse):
            if self.hovered_voivodeship:
                self.hovered_voivodeship = None
                self.needs_redraw = True
            return

        geo_x, geo_y = self._screen_to_geo(mouse)
        pt = Point(geo_x, geo_y)

        hovered = next(
            (v for v in self.voivodeships
             if any(pp.contains(pt) for pp in v['prepared_polygons'])),
            None
        )
        if hovered != self.hovered_voivodeship:
            self.hovered_voivodeship = hovered
            self.needs_redraw = True

    def draw(self, screen: pygame.Surface) -> None:
        """Rysuje mapę na podanym ekranie."""
        if not self.visible:
            return

        if self.needs_redraw or self.cache_surface is None:
            if self.cache_surface is None:
                self.cache_surface = pygame.Surface(
                    (self.rect.width, self.rect.height), pygame.SRCALPHA
                )
                self._draw_base_map()
            self.surface.blit(self.cache_surface, (0, 0))
            self._draw_overlays()
            self.needs_redraw = False

        screen.blit(self.surface, self.rect)

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Obsługuje zdarzenia Pygame (kliknięcia)."""
        if not (self.active and self.visible):
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                local = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                return self.handle_click(local)
        return None

    def handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Obsługuje kliknięcie na mapie, zwraca nazwę województwa lub None."""
        geo_x, geo_y = self._screen_to_geo((pos[0] + self.rect.x, pos[1] + self.rect.y))
        pt = Point(geo_x, geo_y)

        for v in self.voivodeships:
            if any(pp.contains(pt) for pp in v['prepared_polygons']):
                self.selected_voivodeship = v
                print(f"Kliknięto: {v['name']}")
                self.needs_redraw = True
                return v['name']

        self.selected_voivodeship = None
        self.needs_redraw = True
        return None

    def _screen_to_geo(self, pos: Tuple[int, int]) -> Tuple[float, float]:
        """Konwertuje współrzędne ekranu na geograficzne (bazując na rect i mapie)."""
        lx = pos[0] - self.rect.x
        ly = pos[1] - self.rect.y
        sx = self.rect.width / (self.max_x - self.min_x)
        sy = self.rect.height / (self.max_y - self.min_y)
        return (
            self.min_x + lx / sx,
            self.max_y - ly / sy,
        )

    def _draw_base_map(self) -> None:
        """Rysuje statyczną część mapy na cache_surface."""
        sx = self.rect.width / (self.max_x - self.min_x)
        sy = self.rect.height / (self.max_y - self.min_y)
        for v in self.voivodeships:
            for poly in v['polygons']:
                pts = [((x - self.min_x) * sx, (self.max_y - y) * sy)
                       for x, y in poly.exterior.coords]
                pygame.draw.polygon(self.cache_surface, v['color'], pts)
                pygame.draw.polygon(self.cache_surface, (0, 0, 0, 255), pts, 1)
        pygame.draw.rect(self.cache_surface, (0, 0, 0, 255),
                         pygame.Rect(0, 0, self.rect.width, self.rect.height), 2)

    def _draw_overlays(self) -> None:
        """Rysuje elementy hover i zaznaczenia na aktualnej powierzchni."""
        sx = self.rect.width / (self.max_x - self.min_x)
        sy = self.rect.height / (self.max_y - self.min_y)

        for state, key_color, border in [
            (self.hovered_voivodeship, 'hover_color', 1),
            (self.selected_voivodeship, 'color', 2),
        ]:
            if not state:
                continue
            for poly in state['polygons']:
                pts = [((x - self.min_x) * sx, (self.max_y - y) * sy)
                       for x, y in poly.exterior.coords]
                pygame.draw.polygon(self.surface, state[key_color], pts)
                pygame.draw.polygon(self.surface, (0, 0, 0, 255), pts, border)
