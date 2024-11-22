import os
import random
import sys
from pathlib import Path

from PIL import Image


def messageToBits(message):
    return ''.join(f'{ord(c):08b}' for c in message)

def bitsToMessage(bits):
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

def encodeBitsInPixels(pixels, bits, startX, startY, width, height):
    bitIdx = 0
    for y in range(startY, height):
        for x in range(startX if y == startY else 0, width):
            if bitIdx >= len(bits):
                return

            r, g, b = pixels[x, y]

            # Encode one bit in each channel
            if bitIdx < len(bits):
                r = (r & 0b11111110) | int(bits[bitIdx])
                bitIdx += 1
            if bitIdx < len(bits):
                g = (g & 0b11111110) | int(bits[bitIdx])
                bitIdx += 1
            if bitIdx < len(bits):
                b = (b & 0b11111110) | int(bits[bitIdx])
                bitIdx += 1

            pixels[x, y] = (r, g, b)

def decodeBitsFromPixels(pixels, length, startX, startY, width, height):
    bits = ''
    bitIdx = 0
    for y in range(startY, height):
        for x in range(startX if y == startY else 0, width):
            if bitIdx >= length:
                return bits

            r, g, b = pixels[x, y]

            bits += f'{r & 0b00000001:01b}'
            bits += f'{g & 0b00000001:01b}'
            bits += f'{b & 0b00000001:01b}'
            bitIdx += 3

    return bits

# TODO - fix this - function should take into account the random point position and message length  coded at the begining of the message
def countCharacterLimit(imagePath):
    img = Image.open(imagePath)
    result = img.height * img.width
    result = (3 * result) // 8
    return result

def encode(imagePath, message, k):
    img = Image.open(imagePath)
    pixels = img.load()

    bits = messageToBits(message)
    messageLength = len(bits)

    width, height = img.size

    # Get k random starting points and find the best one
    candidates = [(random.randint(0, width-1), random.randint(0, height-1)) for _ in range(k)]
    best_start = None
    fewest_changes = float('inf')

    for start in candidates:
        temp_img = img.copy()
        temp_pixels = temp_img.load()
        
        changes = 0
        bitIdx = 0
        for y in range(start[1], height):
            for x in range(start[0] if y == start[1] else 0, width):
                if bitIdx >= len(bits):
                    break
                r, g, b = temp_pixels[x, y]

                r_change = (r & 0b11111110) != (r & 0b11111110 | int(bits[bitIdx])) if bitIdx < len(bits) else 0
                g_change = (g & 0b11111110) != (g & 0b11111110 | int(bits[bitIdx+1])) if bitIdx+1 < len(bits) else 0
                b_change = (b & 0b11111110) != (b & 0b11111110 | int(bits[bitIdx+2])) if bitIdx+2 < len(bits) else 0

                changes += r_change + g_change + b_change
                bitIdx += 3

        if changes < fewest_changes:
            fewest_changes = changes
            best_start = start

    startX, startY = best_start

    # Encode startX, startY, and message length (32 bits each) in the first few pixels
    metadata_bits = f'{startX:032b}' + f'{startY:032b}' + f'{messageLength:032b}'
    encodeBitsInPixels(pixels, metadata_bits, 0, 0, width, height)

    # Encode the message starting from the best start point
    encodeBitsInPixels(pixels, bits, startX, startY, width, height)

    outputPath = os.path.join(Path(imagePath).parent, Path(imagePath).stem + "_lsbKPoints" + Path(imagePath).suffix)
    img.save(outputPath)
    print(f'Message encoded in {outputPath}')
    return outputPath

def decode(imagePath):
    img = Image.open(imagePath)
    pixels = img.load()

    width, height = img.size

    # Decode the metadata (startX, startY, and message length)
    metadata_bits = decodeBitsFromPixels(pixels, 96, 0, 0, width, height)
    startX = int(metadata_bits[0:32], 2)
    startY = int(metadata_bits[32:64], 2)
    messageLength = int(metadata_bits[64:96], 2)

    # Decode the message starting from the stored starting point
    bits = decodeBitsFromPixels(pixels, messageLength, startX, startY, width, height)
    return bitsToMessage(bits)

def main():
    if len(sys.argv) < 3:
        print('Usage: python ./program.py </path/to/picture> <-c or -d> [k for encoding] [-f <file>]')
        sys.exit(1)

    imagePath = sys.argv[1]
    option = sys.argv[2]

    if option == '-c':
        if len(sys.argv) < 4:
            print('Encoding requires a value for k.')
            sys.exit(1)
        k = int(sys.argv[3])

        if '-f' in sys.argv:
            filePath = sys.argv[sys.argv.index('-f') + 1]
            try:
                with open(filePath, 'r') as file:
                    message = file.read()
                encode(imagePath, message, k)
            except FileNotFoundError:
                print(f'File {filePath} not found.')
        else:
            message = sys.argv[4]
            encode(imagePath, message, k)

    elif option == '-d':
        decodedMessage = decode(imagePath)
        if '-f' in sys.argv:
            outputFile = sys.argv[sys.argv.index('-f') + 1]
            try:
                with open(outputFile, 'w') as file:
                    file.write(decodedMessage)
                print(f'Decoded message saved to {outputFile}')
            except Exception as e:
                print(f'Error saving the message: {e}')
        else:
            print('Decoded message:', decodedMessage)

    else:
        print('Invalid option. Use -c for encoding a message, -f for encoding from a file, -d for decoding, or -d -f for saving the decoded message to a file.')

if __name__ == '__main__':
    main()
