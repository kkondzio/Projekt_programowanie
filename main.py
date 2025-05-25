from PIL import Image
import os
import random

""" Ścieżka do folderu ze zdjęciami """
folder_ze_zdjeciami = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zdjecia")

""" Lista ścieżek do zdjęć w folderze """
lista_zdjec = []
for nazwa_pliku in os.listdir(folder_ze_zdjeciami):
    if nazwa_pliku.lower().endswith(('.jpg', '.jpeg', '.png')):
        sciezka = os.path.join(folder_ze_zdjeciami, nazwa_pliku)
        lista_zdjec.append(sciezka)

""" Funkcja wyświetlająca losowe zdjęcie z folderu """
def pokaz_losowe_zdjecie():
    if lista_zdjec:
        losowe_zdjecie = random.choice(lista_zdjec)
        img = Image.open(losowe_zdjecie)
        img.show()
    else:
        print("Brak zdjęć w folderze.")

if __name__ == "__main__":
    pokaz_losowe_zdjecie()
