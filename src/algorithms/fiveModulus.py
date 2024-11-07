import sys
from PIL import Image
import numpy as np

def squareEncoding(square, letter):
    """
    Encodes a character into a 5x5 square by modifying the red channel values.
    
    Parameters:
    square (numpy array): A 5x5 array representing a portion of the image's red channel.
    letter (str): The character to encode into the square.
    
    Returns:
    numpy array: The modified square with the encoded character.
    """
    letter = ord(letter)
    if letter < 32 or letter > 126:
        print("Error: Message contains an invalid character")
        sys.exit(1)
    reminder = (letter - 31) // 25 + 1
    position = (letter - 31) % 25
    if square[position % 5][position // 5] + reminder > 255: 
        square[position % 5][position // 5] += reminder - 5
    else:
        square[position % 5][position // 5] += reminder
    return square

def squareDecoding(square):
    """
    Decodes a character from a 5x5 square by reading the red channel values.
    
    Parameters:
    square (numpy array): A 5x5 array representing a portion of the image's red channel.
    
    Returns:
    str: The decoded character or '-1' if no character is found.
    """
    for column in range(5):
        for row in range(5): 
            if square[row][column] % 5 != 0:
                reminder = square[row][column] % 5 - 1
                position = column * 5 + row 
                if chr(position + (reminder) * 25 + 31) == "I":
                    print(square)
                return chr(position + (reminder) * 25 + 31)
    return "-1"

def imageToPixels(image_path):
    """
    Loads an image from a file and converts it to a pixel array.
    
    Parameters:
    image_path (str): Path to the image file.
    
    Returns:
    numpy array: Pixel array representing the image.
    """
    image = Image.open(image_path)
    
    # Check format and convert to RGB if RGBA
    if image.mode == 'RGBA':
        print("The image is in RGBA format, converting to RGB...")
        image = image.convert('RGB')
    
    pixels = np.array(image)
    return pixels

def pixelsToImage(pixels, output_image_path):
    """
    Converts a pixel array back into an image and saves it to a file.
    
    Parameters:
    pixels (numpy array): Pixel array representing the image.
    output_image_path (str): Path to save the new image.
    """
    image = Image.fromarray(pixels)
    image.save(output_image_path, format="PNG")
    print(f"Image saved as: {output_image_path}")

def printPixels(pixels):
    """
    Prints the first 10 pixel values from a pixel array.
    
    Parameters:
    pixels (numpy array): Pixel array representing the image.
    """
    print("Pixel content (first 10 pixels):")
    h, w, c = pixels.shape
    for y in range(min(10, h)):
        for x in range(min(10, w)):
            print(f"Pixel ({x}, {y}): {pixels[y, x]}")  # Print RGB values for each pixel

def encode(imagePath, secret_message):
    """
    Encodes a secret message into the red channel of the pixel array by modifying
    red values in blocks of 5x5 pixels.
    
    Parameters:
    imagePath (str): Path to the image
    secret_message (str): The secret message to encode.
    
    Returns:
    Nothing
    """
    pixels = imageToPixels(imagePath)
    secret_message = secret_message.replace("\n", " ")
    if len(pixels.shape) == 3 and pixels.shape[2] == 3:
        red_layer = pixels[:, :, 0]
        
        modified_red_layer = np.round(red_layer / 5) * 5
        
        pixels[:, :, 0] = modified_red_layer.astype(np.uint8)
        height, width, _ = pixels.shape
    
        max_height = (height // 5) * 5
        max_width = (width // 5) * 5
        
        i = 0
        for y in range(0, max_height, 5):
            for x in range(0, max_width, 5):
                square = pixels[y:y+5, x:x+5, 0]
                pixels[y:y+5, x:x+5, 0] = squareEncoding(square, secret_message[i])
                if i == len(secret_message) - 1:
                    break
                i += 1
            if i == len(secret_message) - 1:
                break
    else:
        print("Error: Expected an RGB image.")
    pixelsToImage(pixels, "outputFiveModulus.png") 

def decode(imagePath):
    """
    Decodes a secret message from the red channel of the pixel array by reading 
    the red values in blocks of 5x5 pixels.
    
    Parameters:
    imagePath (str): Path to the image
    
    Returns:
    str: The decoded secret message.
    """
    pixels = imageToPixels(imagePath)
    result = ""
    if len(pixels.shape) == 3 and pixels.shape[2] == 3:
        height, width, _ = pixels.shape
    
        max_height = (height // 5) * 5
        max_width = (width // 5) * 5
        
        i = 0
        letter = ""
        for y in range(0, max_height, 5):
            for x in range(0, max_width, 5):
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
    """
    Main function that processes command-line arguments for encoding or decoding 
    a secret message in an image.
    """
    if len(sys.argv) != 3:
        print("Usage: python program.py [-d <image_path>] or [-e <image_path>]")
        sys.exit(1)
    
    option = sys.argv[1]
    image_path = sys.argv[2]
    
    if option == "-d":
        try:
            pixels = imageToPixels(image_path)
            print(decode(pixels))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif option == "-e":
        try:
            secret_message = input("Enter a secret message to encode in the image: ")
            pixels = encode(image_path, secret_message)
            output_image_path = "output_image.png"
            pixelsToImage(pixels, output_image_path)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print("Invalid option. Use: [-d <image_path>] or [-e <image_path>]")
        sys.exit(1)
