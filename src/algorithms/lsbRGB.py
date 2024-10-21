import sys
from PIL import Image
import os

def message_to_bits(message):
    # Convert the message to a bit string
    bits = ''.join([f'{ord(c):08b}' for c in message])
    return bits

def bits_to_message(bits):
    # Convert the bit string back to the message
    chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

def encode_into_image(img, pixels, bits):
    bit_idx = 0
    for y in range(img.height):
        for x in range(img.width):
            if bit_idx >= len(bits):
                return
            
            r, g, b = pixels[x, y]
            # Hide 2 bits in R, 2 bits in G, and 4 bits in B
            if bit_idx < len(bits):
                r = (r & 0b11111100) | int(bits[bit_idx:bit_idx+2], 2)
                bit_idx += 2
            if bit_idx < len(bits):
                g = (g & 0b11111100) | int(bits[bit_idx:bit_idx+2], 2)
                bit_idx += 2
            if bit_idx < len(bits):
                b = (b & 0b11110000) | int(bits[bit_idx:bit_idx+4], 2)
                bit_idx += 4
            pixels[x, y] = (r, g, b)
    return

def encode_message(image_path, message):
    img = Image.open(image_path)
    pixels = img.load()

    bits = message_to_bits(message)
    message_length = f'{len(bits):032b}'  # 32 bits for the message length
    bits = message_length + bits  # Add message length at the beginning

    encode_into_image(img, pixels, bits)

    # Save the new image with '_encoded' appended to the original file name
    file_name, ext = os.path.splitext(image_path)
    encoded_image_path = f'{file_name}_encoded{ext}'
    img.save(encoded_image_path)
    print(f'Message encoded in {encoded_image_path}')

def decode_message(image_path):
    img = Image.open(image_path)
    pixels = img.load()

    bits = ''
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]

            # Extract 2 bits from R, 2 bits from G, and 4 bits from B
            bits += f'{r & 0b00000011:02b}'
            bits += f'{g & 0b00000011:02b}'
            bits += f'{b & 0b00001111:04b}'

    # Read the message length (first 32 bits)
    message_length = int(bits[:32], 2)
    message_bits = bits[32:32 + message_length]

    return bits_to_message(message_bits)

def main():
    if len(sys.argv) < 3:
        print('Usage: python ./program.py </path/to/picture> <-c or -d> [-f <file>]')
        sys.exit(1)

    image_path = sys.argv[1]
    option = sys.argv[2]

    if option == '-c':
        if '-f' in sys.argv:
            file_path = sys.argv[sys.argv.index('-f') + 1]
            try:
                with open(file_path, 'r') as file:
                    message = file.read()
                encode_message(image_path, message)
            except FileNotFoundError:
                print(f'File {file_path} not found.')
        else:
            message = sys.argv[3]
            encode_message(image_path, message)

    elif option == '-d':
        decoded_message = decode_message(image_path)
        if '-f' in sys.argv:
            output_file = sys.argv[sys.argv.index('-f') + 1]
            try:
                with open(output_file, 'w') as file:
                    file.write(decoded_message)
                print(f'Decoded message saved to {output_file}')
            except Exception as e:
                print(f'Error saving the message: {e}')
        else:
            print('Decoded message:', decoded_message)

    else:
        print('Invalid option. Use -c for encoding a message, -f for encoding from a file, -d for decoding, or -d -f for saving the decoded message to a file.')

if __name__ == '__main__':
    main()
