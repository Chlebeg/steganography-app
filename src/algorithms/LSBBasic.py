import os
import sys
from pathlib import Path

from PIL import Image


def messageToBits(message):
    # Convert the message to a bit string
    bits = ''.join([f'{ord(c):08b}' for c in message])
    return bits

def bitsToMessage(bits):
    # Convert the bit string back to the message
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

def encodeIntoImage(img, pixels, bits):
    bitIdx = 0
    for y in range(img.height):
        for x in range(img.width):
            if bitIdx >= len(bits):
                return
            
            r, g, b = pixels[x, y]
            # Hide 2 bits in R, 2 bits in G, and 4 bits in B
            if bitIdx < len(bits):
                r = (r & 0b11111100) | int(bits[bitIdx:bitIdx+2], 2)
                bitIdx += 2
            if bitIdx < len(bits):
                g = (g & 0b11111100) | int(bits[bitIdx:bitIdx+2], 2)
                bitIdx += 2
            if bitIdx < len(bits):
                b = (b & 0b11110000) | int(bits[bitIdx:bitIdx+4], 2)
                bitIdx += 4
            pixels[x, y] = (r, g, b)
    return

# TODO - fix this - function should take into account the message length coded at the begining of the message
def countCharacterLimit(imagePath):
    img = Image.open(imagePath)
    result = img.height * img.width
    return result

def encode(imagePath, message):
    img = Image.open(imagePath)
    pixels = img.load()

    bits = messageToBits(message)
    messageLength = f'{len(bits):032b}'  # 32 bits for the message length
    print(messageLength)
    bits = messageLength + bits  # Add message length at the beginning

    encodeIntoImage(img, pixels, bits)

    # Save the new image with '_lsbBasic' appended to the original file name
    outputPath = os.path.join(Path(imagePath).parent, Path(imagePath).stem + "_lsbBasic" + Path(imagePath).suffix)
    img.save(outputPath)
    print(f'Message encoded in {outputPath}')
    return outputPath

def decodeFromImage(img, pixels, length):
    bits = ''
    for y in range(img.height):
        for x in range(img.width):
            if length <= len(bits):
                return bits
            r, g, b = pixels[x, y]

            # Extract 2 bits from R, 2 bits from G, and 4 bits from B
            bits += f'{r & 0b00000011:02b}'
            bits += f'{g & 0b00000011:02b}'
            bits += f'{b & 0b00001111:04b}'
    return bits

def decode(imagePath):
    img = Image.open(imagePath)
    pixels = img.load()

    # Read first 32 bits - message length
    bits = ''
    bits += decodeFromImage(img, pixels, 32)
    messageLength = int(bits, 2)
    if messageLength > 1000000:
        return "ERROR"

    # Read the message
    bits = ''
    bits += decodeFromImage(img, pixels, 32+messageLength)
    messageBits = bits[32:32 + messageLength]

    return bitsToMessage(messageBits)

def main():
    if len(sys.argv) < 3:
        print('Usage: python ./program.py </path/to/picture> <-c or -d> [-f <file>]')
        sys.exit(1)

    imagePath = sys.argv[1]
    option = sys.argv[2]

    if option == '-c':
        if '-f' in sys.argv:
            filePath = sys.argv[sys.argv.index('-f') + 1]
            try:
                with open(filePath, 'r') as file:
                    message = file.read()
                encode(imagePath, message)
            except FileNotFoundError:
                print(f'File {filePath} not found.')
        else:
            message = sys.argv[3]
            encode(imagePath, message)

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
