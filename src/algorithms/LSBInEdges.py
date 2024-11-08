import cv2
import sys
import numpy as np

def cannyEdgeDetection(image, thHigh, thLow, kernelSize):
    """Detect edges using Canny edge detection."""
    edges = cv2.Canny(image, thLow, thHigh, apertureSize=kernelSize)
    return edges

def embedMessageInEdges(image, message, edgeMap, key):
    """
    Embed a binary message in the edge pixels of the image using LSB substitution.
    
    Parameters:
    - image: The grayscale or color image (numpy array).
    - message: The binary message to be embedded.
    - edgeMap: The edge map showing where edges are.
    - key: The key for randomizing edge pixel order.
    
    Returns:
    - Modified image with the embedded message.
    """
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

def encode(imagePath,text):
    thHigh = 192
    thLow = 63
    kernelSize = 3
    # Load grayscale image
    image = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)
    processed_image = np.right_shift(image, 2) * 4
    edges = cannyEdgeDetection(processed_image, thHigh, thLow, kernelSize)
    stegoImage = embedMessageInEdges(image, text, edges, key=42)
    extension = imagePath.split("/")[-1].split(".")[1] 
    outputName = "../../photos/" + imagePath.split("/")[-1].split(".")[0] + "_LSBInEdges." + extension
    cv2.imwrite(outputName, stegoImage)

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
    """Show the image with detected edges."""
    edgeImage = np.zeros_like(image)  # Create a blank image
    edgeImage[edges != 0] = 255  # Set edge pixels to white (255)
    
    # Display the edges
    cv2.imshow('Detected Edges', edgeImage)
    cv2.waitKey(0)  # Wait for a key press to close the window
    cv2.destroyAllWindows()

def extractMessageFromEdges(image, edgeMap, key):
    """
    Extract the hidden message from the edge pixels.
    
    Parameters:
    - image: The image with the embedded message.
    - edgeMap: The edge map showing where edges are.
    - messageLength: The length of the message to extract.
    - key: The key for randomizing edge pixel order.randomPermute
    
    Returns:
    - Extracted message.
    """
    np.random.seed(key)  # Set the random seed for reproducibility
    edgePixels = np.argwhere(edgeMap != 0)
    np.random.shuffle(edgePixels)  # Shuffle edge pixels in the same way as during embedding

    binaryMessage = ""

    # Extract the message bits from the edge pixels
    i = 0
    while binaryMessage[-16:] != "1000000000000001":
        print(binaryMessage)
        pixelX, pixelY = edgePixels[i // 2]
        pixelValue = image[pixelX, pixelY]
        # Extract the two least significant bits
        binaryMessage += format(pixelValue & 0b11, '02b')
        i = i + 2
    binaryMessage = binaryMessage[:-16]
    #print(len(binaryMessage)/8)

    # Convert the binary message to a string
    message = ''.join(chr(int(binaryMessage[i:i+8], 2)) for i in range(0, len(binaryMessage), 8))
    return message

# Example usage
if __name__ == "__main__":
    """
    Main function that processes command-line arguments for encoding or decoding 
    a secret message in an image.
    """
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
    

    
    

