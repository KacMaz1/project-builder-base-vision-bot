import cv2
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent

def nic_nie_rob(x):
    pass

# 1. Wczytanie obrazu (Zostawiłem samą nazwę pliku, zakładając, że jesteś w folderze 'test_wizja')
image = cv2.imread(str(HERE / 'wioska_2_1.png'))

# Zabezpieczenie: jeśli skrypt nie znajdzie obrazka, od razu Ci o tym powie
if image is None:
    print("BŁĄD: Nie znaleziono pliku 'wioska_1_1.png'. Upewnij się, że terminal jest w folderze test_wizja!")
    exit()

# 2. Zmniejszenie obrazu, żeby okna nie wyskakiwały poza ekran
image = cv2.resize(image, (1024, 576))

# 3. Przygotowanie głównego okna z suwakami
cv2.namedWindow('Kalibracja')

# Suwaki dla dolnego progu HSV
cv2.createTrackbar('H Min', 'Kalibracja', 0, 179, nic_nie_rob)
cv2.createTrackbar('S Min', 'Kalibracja', 0, 255, nic_nie_rob)
cv2.createTrackbar('V Min', 'Kalibracja', 0, 255, nic_nie_rob)

# Suwaki dla górnego progu HSV
cv2.createTrackbar('H Max', 'Kalibracja', 179, 179, nic_nie_rob)
cv2.createTrackbar('S Max', 'Kalibracja', 255, 255, nic_nie_rob)
cv2.createTrackbar('V Max', 'Kalibracja', 255, 255, nic_nie_rob)

# 4. Konwersja do HSV
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

print("Skrypt odpalony. Przesuwaj suwaki, a na koniec naciśnij 'q' na klawiaturze, żeby zapisać wyniki.")

while True:
    # Pobieranie wartości z suwaków na żywo
    h_min = cv2.getTrackbarPos('H Min', 'Kalibracja')
    s_min = cv2.getTrackbarPos('S Min', 'Kalibracja')
    v_min = cv2.getTrackbarPos('V Min', 'Kalibracja')
    
    h_max = cv2.getTrackbarPos('H Max', 'Kalibracja')
    s_max = cv2.getTrackbarPos('S Max', 'Kalibracja')
    v_max = cv2.getTrackbarPos('V Max', 'Kalibracja')

    lower_bound = np.array([h_min, s_min, v_min])
    upper_bound = np.array([h_max, s_max, v_max])

    # Generowanie maski
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
    
    # Nakładanie maski na oryginał, żeby widzieć co dokładnie łapie
    wynik = cv2.bitwise_and(image, image, mask=mask)

    # Wyświetlanie okien
    cv2.imshow('Maska (Tylko biale miejsca to strefa ataku)', mask)
    cv2.imshow('Wynik z nalezona maska', wynik)

    # Wyjście i zapisanie wartości pod klawiszem 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\n--- TWOJE GOTOWE WARTOŚCI ---")
        print(f"lower_bound = np.array([{h_min}, {s_min}, {v_min}])")
        print(f"upper_bound = np.array([{h_max}, {s_max}, {v_max}])")
        break

cv2.destroyAllWindows()
