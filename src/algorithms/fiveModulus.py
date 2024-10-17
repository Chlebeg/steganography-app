import sys
from PIL import Image
import numpy as np

# Funkcja wczytująca obraz i zwracająca tablicę pikseli
def image_to_pixels(image_path):
    # Otwórz obraz
    image = Image.open(image_path)
    
    # Sprawdź format i konwertuj na RGB, jeśli to RGBA
    if image.mode == 'RGBA':
        print("Obraz jest w formacie RGBA, konwertowanie na RGB...")
        image = image.convert('RGB')
    
    # Konwertuj obraz na tablicę numpy (tablica pikseli)
    pixels = np.array(image)
    return pixels

# Funkcja zamieniająca tablicę pikseli z powrotem na obraz i zapisująca go
def pixels_to_image(pixels, output_image_path):
    # Konwertuj tablicę numpy z powrotem na obiekt Image
    image = Image.fromarray(pixels)
    # Zapisz obraz
    image.save(output_image_path)
    print(f"Obraz zapisano jako: {output_image_path}")

# Funkcja wypisująca zawartość pikseli
def print_pixels(pixels):
    # Jeśli obraz jest RGB, piksele będą miały kształt (wysokość, szerokość, 3)
    print("Zawartość pikseli (pierwsze 10 pikseli):")
    h, w, c = pixels.shape
    for y in range(min(10, h)):
        for x in range(min(10, w)):
            print(f"Pixel ({x}, {y}): {pixels[y, x]}")  # Drukowanie wartości RGB dla każdego piksela

# Główna część programu, która obsługuje argumenty i wykonuje zadania
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie: python program.py <ścieżka_do_obrazu>")
        sys.exit(1)

    # Ścieżka do obrazu podana jako argument
    image_path = sys.argv[1]
    
    try:
        # Konwersja obrazu na tablicę pikseli
        pixels = image_to_pixels(image_path)
        
        # Wypisanie pikseli
        print_pixels(pixels)
        
        # Zapisz obraz z powrotem jako nowy plik
        output_image_path = "output_image.jpg"
        pixels_to_image(pixels, output_image_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
