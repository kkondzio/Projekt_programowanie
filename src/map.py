import pygame
import shapefile
from shapely.geometry import Polygon, Point
from typing import List, Dict, Any, Optional

class PolandMapWidget:
    def __init__(self, x: int, y: int, width: int, height: int, shapefile_path: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.visible: bool = True
        self.active: bool = True
        
        # Wczytaj dane mapy
        self.voivodeships: List[Dict[str, Any]] = []
        self.load_shapefile(shapefile_path)
        self.selected_voivodeship: Optional[Dict[str, Any]] = None
        
    def load_shapefile(self, path: str):
        sf = shapefile.Reader(path)
        shapes = sf.shapes()
        records = sf.records()
        
        self.voivodeships = []
        
        # Znajdź min i max współrzędne dla skalowania
        self.min_x: float = min([min(shape.bbox[0], shape.bbox[2]) for shape in shapes])
        self.max_x: float = max([max(shape.bbox[0], shape.bbox[2]) for shape in shapes])
        self.min_y: float = min([min(shape.bbox[1], shape.bbox[3]) for shape in shapes])
        self.max_y: float = max([max(shape.bbox[1], shape.bbox[3]) for shape in shapes])
        
        # Kolory dla województw
        self.colors: List[tuple[int, int, int, int]] = [
            (255, 0, 0, 150), (0, 255, 0, 150), (0, 0, 255, 150), 
            (255, 255, 0, 150), (255, 0, 255, 150), (0, 255, 255, 150),
            (128, 0, 0, 150), (0, 128, 0, 150), (0, 0, 128, 150),
            (128, 128, 0, 150), (128, 0, 128, 150), (0, 128, 128, 150),
            (192, 192, 192, 150), (128, 128, 128, 150), 
            (153, 153, 255, 150), (153, 51, 102, 150)
        ]
        
        # Przygotuj dane województw
        for i, (shape, record) in enumerate(zip(shapes, records)):
            name: str = record[4] if len(record) > 4 else f"Województwo {i+1}"
            
            polygons: List[Polygon] = []
            parts = list(shape.parts) + [len(shape.points)]
            for j in range(len(parts)-1):
                start = parts[j]
                end = parts[j+1]
                points = shape.points[start:end]
                polygons.append(Polygon(points))
            
            self.voivodeships.append({
                'name': name,
                'polygons': polygons,
                'color': self.colors[i % len(self.colors)]
            })
    
    def update(self) -> None:
        """Aktualizacja stanu mapy"""
        pass
        
    def draw(self, screen: pygame.Surface) -> None:
        """Rysowanie mapy"""
        if not self.visible:
            return
            
        # Wyczyść powierzchnię
        self.surface.fill((0, 0, 0, 0))
        
        # Oblicz skalę
        scale_x: float = self.rect.width / (self.max_x - self.min_x)
        scale_y: float = self.rect.height / (self.max_y - self.min_y)
        
        # Narysuj województwa
        for voivodeship in self.voivodeships:
            color = voivodeship['color']
            if voivodeship == self.selected_voivodeship:
                color = (255, 255, 255, 200)  # Podświetl wybrane
            
            for polygon in voivodeship['polygons']:
                pygame_points: List[tuple[float, float]] = []
                for x, y in polygon.exterior.coords:
                    px = (x - self.min_x) * scale_x
                    py = (self.max_y - y) * scale_y  # Odwracamy y
                    pygame_points.append((px, py))
                
                pygame.draw.polygon(self.surface, color, pygame_points)
                pygame.draw.polygon(self.surface, (0, 0, 0, 255), pygame_points, 1)
        
        # Narysuj ramkę
        pygame.draw.rect(self.surface, (0, 0, 0, 255), 
                        (0, 0, self.rect.width, self.rect.height), 2)
        
        # Wyświetl na głównym ekranie
        screen.blit(self.surface, self.rect)
        
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Obsługa zdarzeń"""
        if not self.active or not self.visible:
            return None
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                local_pos: tuple[int, int] = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                return self.handle_click(local_pos)
                
                
        return None
        
    def handle_click(self, pos: tuple[int, int]) -> Optional[str]:
        """Obsługa kliknięcia na mapie"""
        # Przelicz pozycję na współrzędne geograficzne
        scale_x: float = self.rect.width / (self.max_x - self.min_x)
        scale_y: float = self.rect.height / (self.max_y - self.min_y)
        
        geo_x: float = self.min_x + pos[0] / scale_x
        geo_y: float = self.max_y - pos[1] / scale_y
        
        click_point = Point(geo_x, geo_y)
        
        # Sprawdź które województwo zostało kliknięte
        for voivodeship in self.voivodeships:
            for polygon in voivodeship['polygons']:
                if polygon.contains(click_point):
                    self.selected_voivodeship = voivodeship
                    print(f"Kliknięto: {voivodeship['name']}")
                    return voivodeship['name']
                    
        self.selected_voivodeship = None