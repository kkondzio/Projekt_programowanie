import pygame
import shapefile
from shapely.geometry import Polygon, Point

class PolandMapWidget:
    def __init__(self, x, y, width, height, shapefile_path):
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.visible = True
        self.active = True
        
        # Wczytaj dane mapy
        self.load_shapefile(shapefile_path)
        self.selected_voivodeship = None
        
    def load_shapefile(self, path):
        sf = shapefile.Reader(path)
        shapes = sf.shapes()
        records = sf.records()
        
        self.voivodeships = []
        
        # Znajdź min i max współrzędne dla skalowania
        self.min_x = min([min(shape.bbox[0], shape.bbox[2]) for shape in shapes])
        self.max_x = max([max(shape.bbox[0], shape.bbox[2]) for shape in shapes])
        self.min_y = min([min(shape.bbox[1], shape.bbox[3]) for shape in shapes])
        self.max_y = max([max(shape.bbox[1], shape.bbox[3]) for shape in shapes])
        
        # Kolory dla województw
        self.colors = [
            (255, 0, 0, 150), (0, 255, 0, 150), (0, 0, 255, 150), 
            (255, 255, 0, 150), (255, 0, 255, 150), (0, 255, 255, 150),
            (128, 0, 0, 150), (0, 128, 0, 150), (0, 0, 128, 150),
            (128, 128, 0, 150), (128, 0, 128, 150), (0, 128, 128, 150),
            (192, 192, 192, 150), (128, 128, 128, 150), 
            (153, 153, 255, 150), (153, 51, 102, 150)
        ]
        
        # Przygotuj dane województw
        for i, (shape, record) in enumerate(zip(shapes, records)):
            name = record[4] if len(record) > 4 else f"Województwo {i+1}"
            
            polygons = []
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
    
    def update(self):
        """Aktualizacja stanu mapy"""
        pass
        
    def draw(self, screen):
        """Rysowanie mapy"""
        if not self.visible:
            return
            
        # Wyczyść powierzchnię
        self.surface.fill((0, 0, 0, 0))
        
        # Oblicz skalę
        scale_x = self.rect.width / (self.max_x - self.min_x)
        scale_y = self.rect.height / (self.max_y - self.min_y)
        
        # Narysuj województwa
        for voivodeship in self.voivodeships:
            color = voivodeship['color']
            if voivodeship == self.selected_voivodeship:
                color = (255, 255, 255, 200)  # Podświetl wybrane
            
            for polygon in voivodeship['polygons']:
                pygame_points = []
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
        
    def handle_event(self, event):
        """Obsługa zdarzeń"""
        if not self.active or not self.visible:
            return None
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                local_pos = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                return self.handle_click(local_pos)
                
                
        return None
        
    def handle_click(self, pos):
        """Obsługa kliknięcia na mapie"""
        # Przelicz pozycję na współrzędne geograficzne
        scale_x = self.rect.width / (self.max_x - self.min_x)
        scale_y = self.rect.height / (self.max_y - self.min_y)
        
        geo_x = self.min_x + pos[0] / scale_x
        geo_y = self.max_y - pos[1] / scale_y
        
        click_point = Point(geo_x, geo_y)
        
        # Sprawdź które województwo zostało kliknięte
        for voivodeship in self.voivodeships:
            for polygon in voivodeship['polygons']:
                if polygon.contains(click_point):
                    self.selected_voivodeship = voivodeship
                    print(f"Kliknięto: {voivodeship['name']}")
                    return voivodeship['name']
                    
        self.selected_voivodeship = None