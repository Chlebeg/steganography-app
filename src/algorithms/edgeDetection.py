import cv2
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
    #np.random.seIed(key)  # Set the random seed for reproducibility
    edgePixels = np.argwhere(edgeMap != 0)  # Get coordinates of edge pixels
    #np.random.shuffle(edgePixels)  # Shuffle the edge pixels for random embedding

    # Convert the message into a binary string
    binaryMessage = ''.join(format(ord(char), '08b') for char in message)
    print(binaryMessage)
    
    if len(binaryMessage) > len(edgePixels) * 2:
        raise ValueError("Message too large to embed in the available edge pixels")

    # Embed the message into the edge pixels using LSB substitution
    for i in range(0, len(binaryMessage), 2):
        pixelY, pixelX = edgePixels[i // 2]
        # Modify the two least significant bits in the pixel
        pixelValue = image[pixelX, pixelY]
        # Embed 2 bits of the message
        print(pixelValue)
        newPixelValue = (pixelValue & 0b11111100) | int(binaryMessage[i:i+2], 2)
        image[pixelX, pixelY] = newPixelValue

    return image

def showEdges(image, edges):
    """Show the image with detected edges."""
    edgeImage = np.zeros_like(image)  # Create a blank image
    edgeImage[edges != 0] = 255  # Set edge pixels to white (255)
    
    # Display the edges
    cv2.imshow('Detected Edges', edgeImage)
    cv2.waitKey(0)  # Wait for a key press to close the window
    cv2.destroyAllWindows()

def extractMessageFromEdges(image, edgeMap, messageLength, key):
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
    print(messageLength)
    #np.random.seed(key)  # Set the random seed for reproducibility
    edgePixels = np.argwhere(edgeMap != 0)
    print(edgePixels)
    #np.random.shuffle(edgePixels)  # Shuffle edge pixels in the same way as during embedding

    binaryMessage = ""

    # Extract the message bits from the edge pixels
    for i in range(messageLength * 8):
        pixelX, pixelY = edgePixels[i // 2]
        pixelValue = image[pixelX, pixelY]
        # Extract the two least significant bits
        binaryMessage += format(pixelValue & 0b11, '02b')

    # Convert the binary message to a string
    message = ''.join(chr(int(binaryMessage[i:i+8], 2)) for i in range(0, len(binaryMessage), 8))
    print(len(message))
    return message

# Example usage
if __name__ == "__main__":
    # Load grayscale image
    imagePath = "../../photos/photo1.png"
    image = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)

    # Message to be embedded
    secretMessage = "Marcin"
    
    # Edge detection
    thHigh = 100
    thLow = 90
    kernelSize = 3
    edges = cannyEdgeDetection(image, thHigh, thLow, kernelSize)
    #showEdges(image,edges)
    
    # Embed the message
    stegoImage = embedMessageInEdges(image.copy(), secretMessage, edges, key=42)

    # Save the stego image
    cv2.imwrite("stego_image.png", stegoImage)

    # Extract the message
    extractedMessage = extractMessageFromEdges(stegoImage, edges, len(secretMessage), key=42)
    print(f"Extracted message: {extractedMessage}")
