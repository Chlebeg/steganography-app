import os
import random
import sys
from pathlib import Path

from PIL import Image
   #P = 10007
   #G = 10005
P = 100003
G = 93111

def nextPosition(p = P, g = G):
    position = g
    yield position
    position = (position * g ) % p
    while position != g:
        yield position
        position = (position * g ) % p

def messageToBits(message):
    return ''.join(f'{ord(c):08b}' for c in message)

def bitsToMessage(bits):
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

def encodeBitsInPixels(pixels, bits, width, height, begin=False):
    bitIdx = 0
    positionGenerator = nextPosition()
    
    if len(bits) / 8 > countCharacterLimit():
        print("Too long secret message")
        return
    position = -1
    while bitIdx < len(bits):
        if begin:
            position += 1
            x,y = position,0
        else:
            position = next(positionGenerator)
            x,y = position % width, 1 + position%(height-1)
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

def decodeBitsFromPixels(pixels, length, width, height, begin=False):
    bits = ''
    bitIdx = 0
    positionGenerator = nextPosition()
    position = -1
    while True:
        if begin:
            position += 1
            x,y = position,0
        else:
            position = next(positionGenerator)
            x,y = position % width, 1 + position%(height-1)
        if bitIdx >= length:
            return bits

        r, g, b = pixels[x, y]

        bits += f'{r & 0b00000001:01b}'
        bits += f'{g & 0b00000001:01b}'
        bits += f'{b & 0b00000001:01b}'
        bitIdx += 3

def countCharacterLimit(imagePath=""):
    return (P-1) * 3 // 8 

def encode(imagePath, message):
    img = Image.open(imagePath)
    pixels = img.load()

    bits = messageToBits(message)
    messageLength = len(bits)

    width, height = img.size

    metadata_bits = f'{messageLength:032b}'
    encodeBitsInPixels(pixels, metadata_bits,width, height, True)

    # Encode the message starting from the best start point
    encodeBitsInPixels(pixels, bits, width, height)

    outputPath = os.path.join(Path(imagePath).parent, Path(imagePath).stem + "_lsbWithGenerator" + Path(imagePath).suffix)
    img.save(outputPath)
    print(f'Message encoded in {outputPath}')
    return outputPath

def decode(imagePath):
    img = Image.open(imagePath)
    pixels = img.load()

    width, height = img.size

    metadata_bits = decodeBitsFromPixels(pixels, 32, width, height, True)
    messageLength = int(metadata_bits[0:32], 2)

    bits = decodeBitsFromPixels(pixels, messageLength,width, height)
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
    #main()
    encode("../../photos/photo2.png","Ta1234567890!@#$%^&*()_jna wiadomosc", 20)
    print(decode("../../photos/photo2_lsbWithGenerator.png"))
