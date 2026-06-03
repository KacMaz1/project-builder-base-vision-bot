import cv2
import numpy as np
import pyautogui
import time
import random

# --- KONFIGURACJA Z TWOJEGO KODU (V18.0) ---
VERTICES = [(750, 5), (1200, 5), (1880, 519), (1350, 900), (550, 900), (40, 519)]

CENTER_X = sum([p[0] for p in VERTICES]) // len(VERTICES)
CENTER_Y = sum([p[1] for p in VERTICES]) // len(VERTICES)

def get_red_line_mask(img):
    """
    To jest ta poprawiona funkcja z 'klapkami na oczy'.
    """
    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Zakresy czerwonego
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    full_mask = mask1 + mask2
    
    # --- UI MASKING (To naprawia problem z przyciskiem Surrender) ---
    # Zerujemy dolne 15% ekranu
    ui_bottom_cutoff = int(h * 0.85)
    full_mask[ui_bottom_cutoff:h, :] = 0
    
    # Zerujemy górne 10% ekranu
    ui_top_cutoff = int(h * 0.10)
    full_mask[0:ui_top_cutoff, :] = 0

    # Poprawa jakości
    kernel = np.ones((5,5), np.uint8)
    full_mask = cv2.dilate(full_mask, kernel, iterations=2)
    
    return full_mask

def debug_vision():
    print("Czekam 2 sekundy (przełącz się na grę)...")
    time.sleep(2)
    print("Pobieram zrzut ekranu...")
    
    screen = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
    h, w = screen.shape[:2]
    
    # 1. Obliczanie Maski Bazy (Czerwona Linia)
    red_mask = get_red_line_mask(screen)
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    safe_from_base_mask = np.zeros((h, w), dtype=np.uint8)
    safe_from_base_mask.fill(255) # Białe tło
    
    valid_contours = []
    if contours:
        # Filtracja małych śmieci (pochodni)
        for cnt in contours:
            if cv2.contourArea(cnt) > 1000:
                valid_contours.append(cnt)

    if valid_contours:
        all_points = np.vstack(valid_contours)
        hull = cv2.convexHull(all_points)
        
        # Rysujemy na masce logicznej
        cv2.drawContours(safe_from_base_mask, [hull], -1, 0, thickness=-1)
        safe_from_base_mask = cv2.erode(safe_from_base_mask, np.ones((50, 50), np.uint8), iterations=1)
        
        # Rysujemy na obrazku dla Ciebie (Czerwony obrys bazy)
        cv2.drawContours(screen, [hull], -1, (0, 0, 255), 3) 
    else:
        print("UWAGA: Nie wykryto bazy! Rysuję koło awaryjne.")
        cv2.circle(safe_from_base_mask, (CENTER_X, CENTER_Y), 300, 0, -1)
        cv2.circle(screen, (CENTER_X, CENTER_Y), 300, (0, 0, 255), 3)

    # 2. Obliczanie Maski Vertices (Niebieska Linia)
    vertices_mask = np.zeros((h, w), dtype=np.uint8)
    pts = np.array(VERTICES, np.int32)
    pts = pts.reshape((-1, 1, 2))
    cv2.fillPoly(vertices_mask, [pts], 255)
    
    # Rysujemy niebieski wielokąt
    cv2.polylines(screen, [pts], True, (255, 0, 0), 3)

    # 3. Część Wspólna (FINALNA MASKA)
    final_mask = cv2.bitwise_and(safe_from_base_mask, vertices_mask)
    
    # Nakładamy zielony filtr tam, gdzie bot może klikać
    overlay = screen.copy()
    overlay[final_mask == 255] = [0, 255, 0] # Zielony
    screen = cv2.addWeighted(overlay, 0.3, screen, 0.7, 0)

    # 4. Symulacja Losowania (Żółte Kropki) z logiką sektorów
    print("Symuluję 500 kliknięć z balansem stron...")
    valid_points = cv2.findNonZero(final_mask)
    
    # Rysujemy białą linię środka
    cv2.line(screen, (CENTER_X, 0), (CENTER_X, h), (255, 255, 255), 1)

    if valid_points is not None and len(valid_points) > 0:
        left_side_points = valid_points[valid_points[:, 0, 0] < CENTER_X]
        right_side_points = valid_points[valid_points[:, 0, 0] >= CENTER_X]
        
        for _ in range(500):
            target_list = None
            # Logika 50/50
            if random.random() < 0.5:
                if len(left_side_points) > 0: target_list = left_side_points
                elif len(right_side_points) > 0: target_list = right_side_points
            else:
                if len(right_side_points) > 0: target_list = right_side_points
                elif len(left_side_points) > 0: target_list = left_side_points
            
            if target_list is not None:
                pt = target_list[random.randint(0, len(target_list) - 1)][0]
                cv2.circle(screen, (pt[0], pt[1]), 2, (0, 255, 255), -1)

    # 5. Wyświetlenie (skalowanie dla wygody)
    scale_percent = 60 
    width = int(screen.shape[1] * scale_percent / 100)
    height = int(screen.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(screen, dim, interpolation = cv2.INTER_AREA)

    print("Gotowe. Sprawdź okno podglądu.")
    cv2.imshow("Wizja Bota V18.0 - Debug", resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    debug_vision()