import os
from pathlib import Path
import numpy as np
from PIL import Image


def calculateDifferencingCapacity(difference):
    # Calculate the embedding capacity based on the pixel difference
    if difference < 1:
        return 1
    elif difference < 5:
        return 2
    elif difference < 9:
        return 3
    else:
        return 4

def messageToBits(message):
    return ''.join([f'{ord(c):08b}' for c in message])

def bitsToMessage(bits):
    chars = [chr(int(bits[i:i + 8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

def encode(imagePath, message):
    img = Image.open(imagePath).convert("L")
    pixels = np.array(img)
    messageBits = messageToBits(message) + '0' * 8  # Append end marker
    bitIdx = 0

    # Traverse the image pixels, skip first row and column
    for y in range(1, img.height):
        for x in range(1, img.width):
            if bitIdx >= len(messageBits):
                break

            # Get current pixel and its neighbors
            currentPixel = pixels[y, x]
            leftPixel = pixels[y, x - 1]
            upPixel = pixels[y - 1, x]
            cornerPixel = pixels[y-1,x-1]

            # Calculate pixel value difference
            maxNeighbor = max(leftPixel, upPixel, cornerPixel)
            minNeighbor = min(leftPixel, upPixel, cornerPixel)
            difference = maxNeighbor - minNeighbor
            n = calculateDifferencingCapacity(difference)

            # Embed bits if there are enough remaining
            if bitIdx + n <= len(messageBits):
                # Get the next `n` bits from the message
                dataBits = messageBits[bitIdx:bitIdx + n]
                dataValue = int(dataBits, 2)
                # Modify the pixel value
                newPixelValue = (currentPixel & (0xFF - ((1 << n) - 1))) | dataValue

                # Optimal Pixel Adjustment Process (OPAP)
               #if abs(newPixelValue - currentPixel) > (1 << (n - 1)):
               #    newPixelValue -= 1 if newPixelValue > currentPixel else -1

                pixels[y, x] = newPixelValue
                bitIdx += n

    # Save the modified image
    outputPath = os.path.join(Path(imagePath).parent, Path(imagePath).stem + "_PVD" + Path(imagePath).suffix)
    Image.fromarray(pixels).save(outputPath)
    print(f'Message encoded in {outputPath}')
    return outputPath

def decode(imagePath):
    img = Image.open(imagePath)
    pixels = np.array(img)
    extractedBits = ''

    # Traverse the image pixels, skip first row and column
    for y in range(1, img.height):
        for x in range(1, img.width):
            # Get current pixel and its neighbors
            currentPixel = pixels[y, x]
            leftPixel = pixels[y, x - 1]
            upPixel = pixels[y - 1, x]
            cornerPixel = pixels[y-1,x-1]

            # Calculate pixel value difference
            maxNeighbor = max(leftPixel, upPixel, cornerPixel)
            minNeighbor = min(leftPixel, upPixel, cornerPixel)
            difference = maxNeighbor - minNeighbor
            n = calculateDifferencingCapacity(difference)

            # Extract `n` bits from the current pixel
            extractedBits += f'{currentPixel & ((1 << n) - 1):0{n}b}'
            if '00000000' in extractedBits:
                # Convert bit string to message
                message = bitsToMessage(extractedBits)
                # Find end marker and return the message up to it
                return message.split('\x00', 1)[0]
    return "ERROR WHILE DECODING"

if __name__ == "__main__":
    # Usage example:
    encode("../../photos/photo4.jpg", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaujSecret Message")
    decodedMessage = decode("./../../photos/photo4_PVD.jpg")
    print("Decoded message:", decodedMessage)
