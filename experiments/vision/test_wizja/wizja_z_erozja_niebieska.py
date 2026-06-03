import cv2
import numpy as np
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent

# 1. Twoje wartości skopiowane z terminala:
lower_bound = np.array([108, 88, 75])
upper_bound = np.array([113, 128, 121])

image = cv2.imread(str(HERE / 'wioska_2_2.png'))

if image is None:
    print("Błąd: Nie wczytano obrazu. Sprawdź ścieżkę do pliku.")
    exit()

# 2. Nałożenie filtra kolorów 
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv_image, lower_bound, upper_bound)



# Czyszczenie kropek (Faza 1 i 2 - duży pędzel 15x15)
kernel_duzy = np.ones((60, 60), np.uint8)
czysta_maska = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_duzy)
    
# DODATKOWY MARGINES BEZPIECZEŃSTWA (Faza 3 - mały pędzel 7x7)
kernel_maly = np.ones((10, 10), np.uint8)
czysta_maska = cv2.erode(czysta_maska, kernel_maly, iterations=1)

# 4. WYLOSOWANIE MIEJSCA DO ATAKU
# Teraz funkcja szuka punktów prosto z czystej maski kolorów, bez odcinania krawędzi
biale_punkty = cv2.findNonZero(czysta_maska)

if biale_punkty is not None:
    # Wybiera losowo jeden biały piksel i pobiera jego koordynaty X i Y
    losowy_punkt = random.choice(biale_punkty)[0] 
    print(f"Gotowe! Bot powinien kliknąć w X: {losowy_punkt[0]}, Y: {losowy_punkt[1]}")
    
    # Rysuje czerwoną kropkę na zdjęciu, żebyś widział gdzie bot chce zaatakować
    cv2.circle(image, (losowy_punkt[0], losowy_punkt[1]), 10, (0, 0, 255), -1)
else:
    print("Błąd: Nie znaleziono żadnego wolnego miejsca do ataku na podstawie samych kolorów!")

# Pokaż wynik pracy 
cv2.namedWindow('Maska samych kolorow', cv2.WINDOW_NORMAL)
cv2.namedWindow('Tutaj bot kliknie (czerwona kropka)', cv2.WINDOW_NORMAL)

# Wymuszenie identycznego rozmiaru (szerokość: 800, wysokość: 600)
cv2.resizeWindow('Maska samych kolorow', 800, 600)
cv2.resizeWindow('Tutaj bot kliknie (czerwona kropka)', 800, 600)

cv2.imshow('Maska samych kolorow', czysta_maska)
cv2.imshow('Tutaj bot kliknie (czerwona kropka)', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
