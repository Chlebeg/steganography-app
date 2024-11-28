import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

def squareEncoding(square, letter):
    letter = ord(letter)
    if letter < 32 or letter > 126:
        print("Error: Message contains an invalid character")
        sys.exit(1)
    reminder = (letter - 31) // 25 + 1
    position = (letter - 31) % 25
    result = int(square[position % 5][position // 5])
    if result + reminder > 255: 
        result += reminder - 5
    else:
        result += reminder
    square[position%5][position//5] = result
    return square

def squareDecoding(square):
    for column in range(5):
        for row in range(5): 
            if square[row][column] % 5 != 0:
                reminder = square[row][column] % 5 - 1
                position = column * 5 + row 
                return chr(position + (reminder) * 25 + 31)
    return "-1"

def imageToPixels(imagePath):
    image = Image.open(imagePath)
    
    # Check format and convert to RGB if RGBA
    if image.mode == 'RGBA':
        print("The image is in RGBA format, converting to RGB...")
        image = image.convert('RGB')
    
    pixels = np.array(image)
    return pixels

def pixelsToImage(pixels, outputImagePath):
    image = Image.fromarray(pixels)
    image.save(outputImagePath, format="PNG")
    print(f"Image saved as: {outputImagePath}")

def printPixels(pixels):
    print("Pixel content (first 10 pixels):")
    h, w, c = pixels.shape
    for y in range(min(10, h)):
        for x in range(min(10, w)):
            print(f"Pixel ({x}, {y}): {pixels[y, x]}")  # Print RGB values for each pixel

def countCharacterLimit(imagePath):
    pixels = imageToPixels(imagePath)
    if len(pixels.shape) == 3 and pixels.shape[2] == 3:
        height, width, _ = pixels.shape
    
        result = (height // 5) * (width // 5)  
    return result     
    
def encode(imagePath, secretMessage):
    pixels = imageToPixels(imagePath)
    secretMessage = secretMessage.replace("\n", " ")
    if len(pixels.shape) == 3 and pixels.shape[2] == 3:
        redLayer = pixels[:, :, 0]
        
        modifiedRedLayer = np.round(redLayer / 5) * 5
        
        pixels[:, :, 0] = modifiedRedLayer.astype(np.uint8)
        height, width, _ = pixels.shape
    
        maxHeight = (height // 5) * 5
        maxWidth = (width // 5) * 5
        print(maxHeight," ",maxWidth)
        
        i = 0
        for y in range(0, maxHeight, 5):
            for x in range(0, maxWidth, 5):
                square = pixels[y:y+5, x:x+5, 0]
                pixels[y:y+5, x:x+5, 0] = squareEncoding(square, secretMessage[i])
                if i == len(secretMessage) - 1:
                    break
                i += 1
            if i == len(secretMessage) - 1:
                break
    else:
        print("Error: Expected an RGB image.")
    outputPath = os.path.join(Path(imagePath).parent, Path(imagePath).stem + "_fiveModulus" + Path(imagePath).suffix)
    pixelsToImage(pixels, outputPath)
    return outputPath

def decode(imagePath):
    pixels = imageToPixels(imagePath)
    result = ""
    if len(pixels.shape) == 3 and pixels.shape[2] == 3:
        height, width, _ = pixels.shape
    
        maxHeight = (height // 5) * 5
        maxWidth = (width // 5) * 5
        
        i = 0
        letter = ""
        for y in range(0, maxHeight, 5):
            for x in range(0, maxWidth, 5):
                square = pixels[y:y+5, x:x+5, 0]
                letter = squareDecoding(square)
                if letter == "-1":
                    break
                result += letter
            if letter == "-1":
                break
    else:
        print("Error: Expected an RGB image.")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python program.py [-d <imagePath>] or [-e <imagePath>]")
        sys.exit(1)
    
    option = sys.argv[1]
    imagePath = sys.argv[2]
    
    if option == "-d":
        try:
            pixels = imageToPixels(imagePath)
            print(decode(pixels))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif option == "-e":
        try:
            secretMessage = input("Enter a secret message to encode in the image: ")
            pixels = encode(imagePath, secretMessage)
            outputImagePath = "output_image.png"
            pixelsToImage(pixels, outputImagePath)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print("Invalid option. Use: [-d <imagePath>] or [-e <imagePath>]")
        sys.exit(1)
