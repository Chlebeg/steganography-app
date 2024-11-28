import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

def squaresEncoding(squares, letter):
    letter = ord(letter)
    if letter < 32 or letter > 126:
        print("Error: Message contains an invalid character")
        sys.exit(1)
    reminder = (letter - 31) // 25 + 1
    position = (letter - 31) % 25
    square = position//9
    result = int(squares[square][position % 3][(position - square*9) // 3])
    if result + int(reminder) > 255: 
         result += reminder - 5
    else:
        result += reminder
    squares[square][position % 3][(position - square*9)// 3] = result
    return squares

def squaresDecoding(squares):
    for square in range(3):
        for column in range(3):
            for row in range(3): 
                if squares[square][row][column] % 5 != 0:
                    reminder = squares[square][row][column] % 5 - 1
                    position = 9 * square + column * 3 + row 
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
    
        result = (height // 3) * (width // 3)  
    return result     
    

def encode(imagePath, secretMessage):
    pixels = imageToPixels(imagePath)
    secretMessage = secretMessage.replace("\n", " ")
    if len(pixels.shape) == 3 and pixels.shape[2] == 3:
        redLayer = pixels[:, :, 0]
        greenLayer = pixels[:, :, 1]
        blueLayer = pixels[:, :, 2]
        
        modifiedRedLayer = np.round(redLayer / 5) * 5
        modifiedGreenLayer = np.round(greenLayer / 5) * 5
        modifiedBlueLayer = np.round(blueLayer / 5) * 5
        
        pixels[:, :, 0] = modifiedRedLayer.astype(np.uint8)
        pixels[:, :, 1] = modifiedGreenLayer.astype(np.uint8)
        pixels[:, :, 2] = modifiedBlueLayer.astype(np.uint8)
        height, width, _ = pixels.shape
    
        maxHeight = (height // 3) * 3
        maxWidth = (width // 3) * 3
        
        i = 0
        for y in range(0, maxHeight, 3):
            for x in range(0, maxWidth, 3):
                squares = [pixels[y:y+3, x:x+3, i] for i in range(3)]
                squares = squaresEncoding(squares, secretMessage[i])
                pixels[y:y+3, x:x+3, 0] = squares[0]
                pixels[y:y+3, x:x+3, 1] = squares[1]
                pixels[y:y+3, x:x+3, 2] = squares[2]
                if i == len(secretMessage) - 1:
                    break
                i += 1
            if i == len(secretMessage) - 1:
                break
    else:
        print("Error: Expected an RGB image.")
    outputPath = os.path.join(Path(imagePath).parent, Path(imagePath).stem + "_fiveModulusWithTwist" + Path(imagePath).suffix)
    pixelsToImage(pixels, outputPath)
    return outputPath

def decode(imagePath):
    pixels = imageToPixels(imagePath)
    result = ""
    if len(pixels.shape) == 3 and pixels.shape[2] == 3:
        height, width, _ = pixels.shape
    
        maxHeight = (height // 3) * 3
        maxWidth = (width // 3) * 3
        
        i = 0
        letter = ""
        for y in range(0, maxHeight, 3):
            for x in range(0, maxWidth, 3):
                squares = [ pixels[y:y+3, x:x+3, i] for i in range(3)]
                letter = squaresDecoding(squares)
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
            print(decode(imagePath))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif option == "-e":
        try:
            secretMessage = input("Enter a secret message to encode in the image: ")
            encode(imagePath, secretMessage)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print("Invalid option. Use: [-d <imagePath>] or [-e <imagePath>]")
        sys.exit(1)