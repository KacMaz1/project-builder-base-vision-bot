import cv2
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Wpisz tutaj ścieżkę do swojego zrzutu ekranu (zielonej lub niebieskiej bazy)
sciezka_do_zdjecia = HERE / 'do_przetestowania1.png'  # Zmien na 'wioska_2_1.png' dla niebieskiej bazy

image = cv2.imread(str(sciezka_do_zdjecia))

if image is None:
    print(f"Błąd: Nie można wczytać pliku {sciezka_do_zdjecia}. Sprawdź ścieżkę!")
else:
    # Konwersja na HSV i wyliczenie średniej
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    srednie_hsv = cv2.mean(hsv_image)
    sredni_odcien = srednie_hsv[0]

    print(f"--- WYNIK DLA: {sciezka_do_zdjecia} ---")
    print(f"Średni odcień (H): {sredni_odcien:.2f}")
    
    # Próbny próg dla testu - możesz go potem dostroić w głównym bocie
    if sredni_odcien > 85:
        print("Werdykt algorytmu: Baza NIEBIESKA")
    else:
        print("Werdykt algorytmu: Baza ZIELONA")
