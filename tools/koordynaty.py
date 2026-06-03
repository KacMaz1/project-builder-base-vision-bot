import pyautogui
import time

print("--- LOKALIZATOR KURSORA ---")
print("Naciśnij Ctrl+C w konsoli, aby zatrzymać.")

try:
    while True:
        x, y = pyautogui.position()
        # \r powoduje nadpisywanie jednej linii, żeby nie śmiecić w konsoli
        print(f"Aktualna Pozycja: X={x}, Y={y}    ", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nZakończono.")