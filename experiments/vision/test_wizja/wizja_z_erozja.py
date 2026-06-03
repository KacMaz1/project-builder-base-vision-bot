import cv2
import numpy as np
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent

# 1. Twoje wartości skopiowane z terminala:
lower_bound = np.array([66, 68, 76])
upper_bound = np.array([99, 104, 144])

image = cv2.imread(str(HERE / 'do_przetestowania2_zielona.png'))

if image is None:
    print("Błąd: Nie wczytano obrazu. Sprawdź ścieżkę do pliku.")
    exit()

# 2. Nałożenie filtra kolorów 
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

# 3. USUWANIE BIAŁYCH KROPEK (Otwarcie morfologiczne)
# Zwiększamy pędzel z 5x5 na np. 15x15 (jeśli kropki dalej będą, wpisz tu nawet 25x25)
kernel = np.ones((15, 15), np.uint8)

# Operacja otwarcia - wymazuje małe śmieci i zostawia duże obszary
czysta_maska = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

# DODATKOWY MARGINES BEZPIECZEŃSTWA:
# Jeśli chcesz, żeby bot trzymał się trochę dalej od murów i budynków 
# (aby nie kliknął idealnie na krawędzi strefy), odkomentuj poniższą linijkę:
# czysta_maska = cv2.erode(czysta_maska, kernel, iterations=1)

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

# Pokaż wynik pracy (dodane formatowanie okien, żeby można było je zmniejszać)
cv2.namedWindow('Maska samych kolorow', cv2.WINDOW_NORMAL)
cv2.namedWindow('Tutaj bot kliknie (czerwona kropka)', cv2.WINDOW_NORMAL)
cv2.imshow('Maska samych kolorow', czysta_maska)
cv2.imshow('Tutaj bot kliknie (czerwona kropka)', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
