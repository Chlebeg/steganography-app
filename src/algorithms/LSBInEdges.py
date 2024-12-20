import os
import sys
from pathlib import Path

import cv2
import numpy as np


def cannyEdgeDetection(image, thHigh, thLow, kernelSize):
    edges = cv2.Canny(image, thLow, thHigh, apertureSize=kernelSize)
    return edges

def embedMessageInEdges(image, message, edgeMap, key):
    np.random.seed(key)  # Set the random seed for reproducibility
    edgePixels = np.argwhere(edgeMap != 0)  # Get coordinates of edge pixels
    np.random.shuffle(edgePixels)  # Shuffle the edge pixels for random embedding

    # Convert the message into a binary string
    binaryMessage = ''.join(format(ord(char), '08b') for char in message)
    binaryMessage += "1000000000000001"
    
    if len(binaryMessage) > len(edgePixels) * 2:
        raise ValueError("Message too large to embed in the available edge pixels")

    # Embed the message into the edge pixels using LSB substitution
    for i in range(0, len(binaryMessage), 2):
        pixelX, pixelY = edgePixels[i // 2]
        # Modify the two least significant bits in the pixel
        pixelValue = image[pixelX, pixelY]
        # Embed 2 bits of the message
        newPixelValue = (pixelValue & 0b11111100) | int(binaryMessage[i:i+2], 2)
        image[pixelX, pixelY] = newPixelValue

    return image

def countCharacterLimit(imagePath):
    thHigh = 192
    thLow = 63
    kernelSize = 3
    # Load grayscale image
    image = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)
    processed_image = np.right_shift(image, 2) * 4
    edges = cannyEdgeDetection(processed_image, thHigh, thLow, kernelSize)
    edgePixels = np.argwhere(edges != 0)  # Get coordinates of edge pixels
    result = len(edgePixels)//4-2 
    return result

def encode(imagePath,text):
    thHigh = 192
    thLow = 63
    kernelSize = 3
    # Load grayscale image
    image = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)
    processed_image = np.right_shift(image, 2) * 4
    edges = cannyEdgeDetection(processed_image, thHigh, thLow, kernelSize)
    stegoImage = embedMessageInEdges(image, text, edges, key=42)
    
    outputPath = os.path.join(Path(imagePath).parent, Path(imagePath).stem + "_lsbInEdges" + Path(imagePath).suffix)
    cv2.imwrite(outputPath, stegoImage)
    print(f'Message encoded in {outputPath}')
    return outputPath

def decode(imagePath):
    thHigh = 192
    thLow = 63
    kernelSize = 3
    # Load grayscale image
    image = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)
    processed_image = np.right_shift(image, 2) * 4
    edges = cannyEdgeDetection(processed_image, thHigh, thLow, kernelSize)
    extractedMessage = extractMessageFromEdges(image, edges, key=42)
    return extractedMessage

def showEdges(image, edges):
    edgeImage = np.zeros_like(image)  # Create a blank image
    edgeImage[edges != 0] = 255  # Set edge pixels to white (255)
    
    # Display the edges
    cv2.imshow('Detected Edges', edgeImage)
    cv2.waitKey(0)  # Wait for a key press to close the window
    cv2.destroyAllWindows()

def extractMessageFromEdges(image, edgeMap, key):
    np.random.seed(key)  # Set the random seed for reproducibility
    edgePixels = np.argwhere(edgeMap != 0)
    np.random.shuffle(edgePixels)  # Shuffle edge pixels in the same way as during embedding

    binaryMessage = ""

    # Extract the message bits from the edge pixels
    i = 0
    while binaryMessage[-16:] != "1000000000000001":
        pixelX, pixelY = edgePixels[i // 2]
        pixelValue = image[pixelX, pixelY]
        # Extract the two least significant bits
        binaryMessage += format(pixelValue & 0b11, '02b')
        i = i + 2
    binaryMessage = binaryMessage[:-16]

    # Convert the binary message to a string
    message = ''.join(chr(int(binaryMessage[i:i+8], 2)) for i in range(0, len(binaryMessage), 8))
    return message

if __name__ == "__main__":
    # Edge detection
    thHigh = 192
    thLow = 63
    kernelSize = 3
    if len(sys.argv) != 3:
        print("Usage: python program.py [-d <image_path>] or [-e <image_path>]")
        sys.exit(1)
    
    option = sys.argv[1]
    image_path = sys.argv[2]
    # Load grayscale image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    processed_image = np.right_shift(image, 2) * 4
    edges = cannyEdgeDetection(processed_image, thHigh, thLow, kernelSize)
    #showEdges(image,edges)
    
    if option == "-d":
        try:
            secretMessage = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            # Extract the message
            extractedMessage = extractMessageFromEdges(image, edges, key=42)
            print(f"Extracted message: {extractedMessage}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif option == "-e":
        try:
            secret_message = input("Enter a secret message to encode in the image: ")
            # Embed the message
            stegoImage = embedMessageInEdges(image, secret_message, edges, key=42)
            output_image_path = "output_image.png"
            print(extractMessageFromEdges(stegoImage,edges,42))
            # Save the stego image
            cv2.imwrite(output_image_path, stegoImage)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print("Invalid option. Use: [-d <image_path>] or [-e <image_path>]")
        sys.exit(1)