import cv2
import numpy as np
import pyautogui
import time
import random
import sys
import math
import serial
from pathlib import Path

# ==============================================================================
#                 vvv  KONFIGURACJA (PARAMETRY)  vvv
# ==============================================================================

PICO_PORT = 'COM11' 

BATTLE_DURATION_SECONDS = (80, 17) 
END_TRIGGER_POS = (1219, 991) 
BD_COUNTS = [6, 7,]           
BD_WEIGHTS = [0.7, 0.3,] 
MAX_RUNTIME_MINUTES = (160, 161)
COLLECT_EVERY_N_ATTACKS = (2, 3) 
CONFIDENCE_LEVEL = 0.8           
TRIGGER_CONFIDENCE = 0.85   

GRAY_DRAGON_CONFIDENCE = 0.65 
SATURATION_THRESHOLD = 35 

ACTIVE_DRAGON_CLICK_CONFIDENCE = 0.55
TAKE_BREAK_EVERY_MINUTES = (15, 30) 
BREAK_DURATION_SECONDS = (40, 90)  

# ==============================================================================
#                 ^^^  KONIEC KONFIGURACJI  ^^^
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = PROJECT_ROOT / "assets" / "templates"

pyautogui.PAUSE = 0 
pyautogui.FAILSAFE = False

try:
    ser = serial.Serial(PICO_PORT, 115200, timeout=0.05)
    print(f"Połączono z Pico na porcie {PICO_PORT} - V70.0 WIZJA KOLORÓW")
except Exception as e:
    print(f"BŁĄD PICO: {e}")
    sys.exit()

SESSION_LIMIT = random.randint(*MAX_RUNTIME_MINUTES)
START_TIME = time.time()
last_break_time = time.time()
next_break_in = random.randint(*TAKE_BREAK_EVERY_MINUTES) * 60
attack_counter = 0
next_collect_at = random.randint(*COLLECT_EVERY_N_ATTACKS)

# Automatyczny środek ekranu (zastępuje VERTICES dla zbierania eliksiru)
SCREEN_W, SCREEN_H = pyautogui.size()
CENTER_X = SCREEN_W // 2
CENTER_Y = SCREEN_H // 2

# --- FUNKCJA DO CZASÓW ---

def sleep_human(min_s, max_s):
    if min_s >= max_s:
        time.sleep(min_s)
        return
    diff = max_s - min_s
    mnoznik = np.random.lognormal(0, 0.4)
    val = min_s + (mnoznik * (diff / 2.0))
    val = min(val, min_s + (diff * 2.5))
    time.sleep(val)

# --- FUNKCJE SPRZĘTOWE PICO ---

def pico_send(cmd):
    try: ser.write(f"{cmd}\n".encode())
    except: pass

def pico_move_raw(dx, dy):
    if dx == 0 and dy == 0: return
    pico_send(f"M {int(dx)} {int(dy)}")

def pico_click():
    pico_send("C")
    sleep_human(0.08, 0.15)

def pico_down(): pico_send("D")
def pico_up(): pico_send("U")

def wind_mouse_movement(start_x, start_y, dest_x, dest_y, G_0=8, W_0=3, M_0=10, D_0=12):
    current_x, current_y = start_x, start_y
    sqrt3 = np.sqrt(3)
    DAMPING = 0.42 
    v_x, v_y, W_x, W_y = 0, 0, 0, 0
    dist = math.hypot(dest_x - start_x, dest_y - start_y)
    while dist > 5:
        real_x, real_y = pyautogui.position()
        if math.hypot(current_x - real_x, current_y - real_y) > 30:
            current_x, current_y = real_x, real_y
        dist = math.hypot(dest_x - current_x, dest_y - current_y)
        if dist < 5: break
        W_x = W_x / sqrt3 + (random.random() - 0.5) * W_0
        W_y = W_y / sqrt3 + (random.random() - 0.5) * W_0
        if dist != 0:
            G_x = (dest_x - current_x) / dist * G_0
            G_y = (dest_y - current_y) / dist * G_0
        else: G_x, G_y = 0, 0
        v_x += W_x + G_x
        v_y += W_y + G_y
        vel_mag = math.hypot(v_x, v_y)
        if vel_mag > M_0:
            v_x, v_y = (v_x / vel_mag) * M_0, (v_y / vel_mag) * M_0
        if dist < D_0:
             v_x *= (dist / D_0)
             v_y *= (dist / D_0)
        target_step_x, target_step_y = current_x + v_x, current_y + v_y
        move_x = int((target_step_x - real_x) * DAMPING)
        move_y = int((target_step_y - real_y) * DAMPING)
        if abs(move_x) >= 1 or abs(move_y) >= 1:
            pico_move_raw(move_x, move_y)
        current_x, current_y = target_step_x, target_step_y
        time.sleep(0.008)
    time.sleep(0.05)
    for _ in range(3):
        rx, ry = pyautogui.position()
        dx, dy = dest_x - rx, dest_y - ry
        if abs(dx) < 3 and abs(dy) < 3: break
        pico_move_raw(1 if dx > 0 else -1 if dx < 0 else 0, 1 if dy > 0 else -1 if dy < 0 else 0)
        time.sleep(0.02)

def ultra_human_move(cel_x, cel_y):
    start_x, start_y = pyautogui.position()
    wind_mouse_movement(start_x, start_y, cel_x, cel_y)

def smart_click(x, y):
    ultra_human_move(x, y)
    sleep_human(0.15, 0.3) 
    pico_click()

def ultra_human_drag(start_x, start_y, end_x, end_y):
    ultra_human_move(start_x, start_y)
    sleep_human(0.15, 0.25)
    pico_down()
    sleep_human(0.15, 0.25)
    wind_mouse_movement(start_x, start_y, end_x, end_y, G_0=6, W_0=1, M_0=8)
    sleep_human(0.15, 0.20)
    pico_up()

def find_and_click(image_name, confidence=CONFIDENCE_LEVEL, region=None, click=True):
    template = cv2.imread(str(TEMPLATE_DIR / image_name))
    if template is None: return False
    screen = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
    rx, ry = (region[0], region[1]) if region else (0, 0)
    rw, rh = (region[2], region[3]) if region else (screen.shape[1], screen.shape[0])
    res = cv2.matchTemplate(screen[ry:ry+rh, rx:rx+rw], template, cv2.TM_CCOEFF_NORMED)
    _, mv, _, ml = cv2.minMaxLoc(res)
    
    if mv >= confidence:
        if click:
            h, w = template.shape[:2]
            if "helicopter" in image_name or "baby_dragon" in image_name:
                off_x = np.clip(np.random.normal(w/2, w/6), w*0.2, w*0.8)
                off_y = np.clip(np.random.normal(h*0.3, h*0.08), h*0.1, h*0.4) 
            else:
                off_x = np.clip(np.random.normal(w/2, w/5), w*0.1, w*0.9)
                off_y = np.clip(np.random.normal(h/2, h*0.15), h*0.2, h*0.8)
            smart_click(int(ml[0] + rx + off_x), int(ml[1] + ry + off_y))
        return True
    return False

# ==============================================================================
#                 vvv  NOWA WIZJA KOLORÓW  vvv
# ==============================================================================

def get_safe_spawn_point():
    # Pobieramy pełny zrzut ekranu
    screen = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
    
    # Konwersja do HSV, żeby łatwo wyciągnąć sam "kolor" (Hue)
    hsv_image = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
    
    # cv2.mean oblicza średnią dla całego obrazka. Wynik to: (Średnie H, Średnie S, Średnie V, 0)
    srednie_hsv = cv2.mean(hsv_image)
    sredni_odcien = srednie_hsv[0]  # Interesuje nas tylko pierwszy parametr, czyli odcień (H)
    
    # W OpenCV odcień (H) jest w skali od 0 do 179.
    # Zielona trawa daje średnią ok. 40-70. Niebieska nocna mapa podbija średnią powyżej 90-100.
    print(f"DEBUG: Średni odcień mapy to: {sredni_odcien:.1f}")
    
    if sredni_odcien > 90:  # Próg odcięcia. Wszystko powyżej 85 traktujemy jako niebieską bazę
        is_blue = True
    else:
        is_blue = False
        
    if is_blue:
        lower_bound = np.array([108, 88, 75])
        upper_bound = np.array([119, 149, 123])
    else:
        lower_bound = np.array([66, 68, 76])
        upper_bound = np.array([99, 104, 144])

    # Filtracja kolorów
    hsv_image = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

    # Czyszczenie kropek (Faza 1 i 2 - duży pędzel 15x15)
    kernel_duzy = np.ones((60, 60), np.uint8)
    czysta_maska = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_duzy)
    
    # DODATKOWY MARGINES BEZPIECZEŃSTWA (Faza 3 - mały pędzel 7x7)
    kernel_maly = np.ones((10, 10), np.uint8)
    czysta_maska = cv2.erode(czysta_maska, kernel_maly, iterations=1)

    # Pobieranie białych punktów (bezpiecznych miejsc)
    biale_punkty = cv2.findNonZero(czysta_maska)

    if biale_punkty is not None:
        losowy_punkt = random.choice(biale_punkty)[0]
        return int(losowy_punkt[0]), int(losowy_punkt[1])
    else:
        print("UWAGA: Wizja nie znalazła punktów! Zrzucam blisko środka.")
        return CENTER_X, CENTER_Y

# ==============================================================================
#                 ^^^  NOWA WIZJA KOLORÓW  ^^^
# ==============================================================================

def count_gray_dragons():
    template = cv2.imread(str(TEMPLATE_DIR / "szary_smok.png"))
    if template is None: return 0
    screen = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
    img_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    tmpl_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    img_hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
    saturation_channel = img_hsv[:, :, 1]
    res = cv2.matchTemplate(img_gray, tmpl_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= GRAY_DRAGON_CONFIDENCE)
    w, h = tmpl_gray.shape[::-1]
    rectangles = []
    for pt in zip(*loc[::-1]):
        x, y = int(pt[0]), int(pt[1])
        center_x = x + w // 2
        center_y = y + h // 2
        try:
            roi_sat = saturation_channel[center_y-5:center_y+5, center_x-5:center_x+5]
            avg_sat = np.mean(roi_sat)
        except: avg_sat = 0
        if avg_sat < SATURATION_THRESHOLD:
            rectangles.append([x, y, w, h])
            rectangles.append([x, y, w, h])
    rects, _ = cv2.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
    return len(rects)

def check_for_afk_break():
    global last_break_time, next_break_in
    if time.time() - last_break_time > next_break_in:
        break_duration = random.randint(*BREAK_DURATION_SECONDS)
        print(f"--- CZAS NA PRZERWĘ! ({break_duration}s) ---")
        start_break = time.time()
        while time.time() - start_break < break_duration:
            if random.random() < 0.05:
                pico_move_raw(random.randint(-80, 80), random.randint(-90, 72))
            time.sleep(1)
        print("--- KONIEC PRZERWY ---")
        last_break_time = time.time()
        next_break_in = random.randint(*TAKE_BREAK_EVERY_MINUTES) * 60

def collect_elixir_routine():
    print("--- ZBIERANIE ELIKSIRU ---")
    s_x = CENTER_X + random.randint(-400, 400)
    s_y = CENTER_Y - random.randint(100, 300)
    e_x = s_x + random.randint(-300, 300)
    e_y = s_y + random.randint(350, 650)
    ultra_human_drag(s_x, s_y, e_x, e_y)
    sleep_human(1.5, 2.2)
    
    if find_and_click("wozek.png", 0.65) or find_and_click("wozek_walka.png", 0.65) or find_and_click('wozek_walka_pelny.png') or find_and_click("wozek_pelny.png"):
        sleep_human(1.0, 1.5)
        find_and_click("collect.png", 0.75)
        sleep_human(0.8, 1.4)
        find_and_click("close_x.png", 0.75)
        sleep_human(0.7, 1.2)

def deploy_phase_2():
    print("Faza 2: Intelligent Deployment")
    sleep_human(2.0, 3.0)
    if find_and_click("helicopter.png", 0.6):
        sleep_human(0.3, 0.4)
        tx, ty = get_safe_spawn_point()
        smart_click(tx, ty)
        sleep_human(0.6, 0.9)
    gray_count = count_gray_dragons()
    to_deploy = 8 - gray_count
    print(f"DEBUG: Wykryto szarych: {gray_count}. Teoretycznie do zrzutu: {to_deploy}")
    if to_deploy <= 0:
        to_deploy = 2
    to_deploy = min(8, to_deploy)
    print(f"FINALNIE ZRZUCAM: {to_deploy} smoków.")
    if to_deploy > 0:
        if find_and_click("baby_dragon.png", ACTIVE_DRAGON_CLICK_CONFIDENCE):
            for i in range(to_deploy):
                tx, ty = get_safe_spawn_point() 
                smart_click(tx, ty)
                if i < 2: sleep_human(0.18, 0.35)
                else: sleep_human(0.14, 0.25)
        else:
            print("BŁĄD: Nie mogę znaleźć kolorowej karty smoka!")

def battle_loop():
    global attack_counter
    print("Atak Faza 1...")
    if find_and_click("helicopter.png", 0.7):
        sleep_human(0.3, 0.5)
        tx, ty = get_safe_spawn_point()
        smart_click(tx, ty)
        sleep_human(0.8, 1.2)
    if find_and_click("baby_dragon.png", 0.7):
        count = random.choices(BD_COUNTS, BD_WEIGHTS)[0]
        for _ in range(count):
            tx, ty = get_safe_spawn_point()
            smart_click(tx, ty)
            sleep_human(0.18, 0.40)
    
    start = time.time()
    limit = max(5, np.random.normal(BATTLE_DURATION_SECONDS[0], BATTLE_DURATION_SECONDS[1]))
    print(f"Limit czasu: {limit:.1f}s")
    
    phase_2_done = False
    
    while (time.time() - start) < limit:
        if find_and_click("return_home.png", 0.8, click=False):
            print("Wygrana / Koniec wojska.")
            break
        if not phase_2_done and find_and_click("baby_dragon.png", TRIGGER_CONFIDENCE, (END_TRIGGER_POS[0]-20, END_TRIGGER_POS[1]-20, 40, 40), False):
            print("Trigger Faza 2!")
            deploy_phase_2()
            phase_2_done = True
        time.sleep(1)
    
    print("Poddawanie (Licznik 5 prób)...")
    attempts = 0
    while not find_and_click("return_home.png", 0.75):
        attempts += 1
        print(f"Próba wyjścia: {attempts}/5")
        
        if attempts > 5:
            print("KRYTYCZNY BŁĄD: Gra nie reaguje. Zamykam program!")
            sys.exit()
            
        if find_and_click("surrender.png", 0.8):
            sleep_human(0.5, 0.8)
        elif find_and_click("end_battle.png", 0.8):
            sleep_human(0.5, 0.8)
            
        if find_and_click("zielony_ok.png", 0.8):
            sleep_human(0.5, 0.8)
            
        sleep_human(1.8, 2.5)
        
    attack_counter += 1
    print("Koniec.")

def main():
    global attack_counter, next_collect_at
    print(f"V70.0 WIZJA KOLORÓW START")
    while (time.time() - START_TIME) / 60 < SESSION_LIMIT:
        check_for_afk_break()
        if attack_counter >= next_collect_at:
            collect_elixir_routine()
            attack_counter, next_collect_at = 0, random.randint(*COLLECT_EVERY_N_ATTACKS)
            sleep_human(2.0, 3.5)
        if find_and_click("attack2.png", 0.6):
            sleep_human(1.2, 1.8)
            if find_and_click("find_now.png", 0.85):
                sleep_human(8.0, 12.0)
                battle_loop()
        if random.random() < 0.15:
            ultra_human_move(random.randint(300, SCREEN_W-100), random.randint(250, SCREEN_H-100))
            sleep_human(2.5, 7.5)
            ultra_human_move(random.randint(300, SCREEN_W-100), random.randint(250, SCREEN_H-100))
        sleep_human(4.5, 7.5)

if __name__ == "__main__":
    main()
