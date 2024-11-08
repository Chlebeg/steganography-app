import LSBInEdges as lsbE
import fiveModulus as fm
import lsbRGB as lsbRGB
import PVD as pvd
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import numpy as np
import cv2  # OpenCV do obliczeń PSNR, MSE

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganografia")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(sticky="nsew", padx=10, pady=10)

        # Tworzenie zakładek
        self.tabs = []
        self.textEntries = {}  
        self.imagePaths = {}    
        self.imagePathLabels = {}
        tabsName = ["LSB", "FiveModulus", "EdgeLSB", "PVD", "Comparison"]

        for i in range(len(tabsName)):
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=tabsName[i])
            self.tabs.append(tab)
            if tabsName[i] == "Comparison":
                self.createComparisonTab(tab)
            else:
                self.createTab(tab, tabsName[i])

    def createTab(self, tab, tabsName):
        # Configure grid weights to make elements inside the tab responsive
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)

        # Encoding and decoding buttons (at the top)
        buttonFrame = tk.Frame(tab)
        buttonFrame.grid(row=0, column=0, pady=10, sticky="ew")
        buttonFrame.columnconfigure(0, weight=1)
        buttonFrame.columnconfigure(1, weight=1)
        buttonFrame.columnconfigure(2, weight=0)  # For the Info button

        encodeButton = tk.Button(buttonFrame, text="Kodowanie", width=20, command=lambda: self.encode(tabsName))
        decodeButton = tk.Button(buttonFrame, text="Dekodowanie", width=20, command=lambda: self.decode(tabsName))
        
        # Move the info button to the middle
        infoButton = tk.Button(buttonFrame, text="Info", command=lambda: self.showInfo())

        encodeButton.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
        infoButton.grid(row=0, column=1, padx=20, pady=5, sticky="ew")  # Place it between Kodowanie and Dekodowanie
        decodeButton.grid(row=0, column=2, padx=20, pady=5, sticky="ew")

        # Containers for text input and image selection
        mainFrame = tk.Frame(tab)
        mainFrame.grid(row=1, column=0, pady=10, sticky="nsew")
        mainFrame.columnconfigure(0, weight=1)
        mainFrame.columnconfigure(1, weight=3)

        # Text entry field for encoding (specific to this tab)
        textEntry = tk.Text(mainFrame, height=5, width=40)
        textEntry.grid(row=0, column=1, padx=20, sticky="nsew")
        self.textEntries[tabsName] = textEntry  # Store the text entry for this tab

        # Button to select image
        selectImageButton = tk.Button(tab, text="Wybierz zdjęcie", command=lambda: self.selectImage(tabsName))
        selectImageButton.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

        # Label to show the selected image's path (specific to this tab)
        imagePathLabel = tk.Label(tab, text="", fg="blue")
        imagePathLabel.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.imagePathLabels[tabsName] = imagePathLabel  # Store the label for this tab

        # Initialize image path for this tab
        self.imagePaths[tabsName] = ""  # Store the image path for this tab

    def showInfo(self):
        # Create a new Toplevel window for the info
        infoWindow = tk.Toplevel(self.root)
        infoWindow.title("Informacje")
        
        # Create a label with information text
        infoText = tk.Label(infoWindow, text="This is an application for steganography.\n\n"
                                            "Use the buttons to encode or decode messages in images.\n"
                                            "Select an image using 'Wybierz zdjęcie' button.")
        infoText.pack(padx=20, pady=20)

        # Add a close button
        closeButton = tk.Button(infoWindow, text="Close", command=infoWindow.destroy)
        closeButton.pack(pady=5)

    def createComparisonTab(self, tab):
        # Zakładka porównania obrazów
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)

        # Kontenery dla obrazów i statystyk
        imageFrame = tk.Frame(tab)
        imageFrame.grid(row=0, column=0, pady=10, sticky="nsew")
        imageFrame.columnconfigure(0, weight=1)
        imageFrame.columnconfigure(1, weight=1)

        # Wybór obrazów
        self.originalImagePath = ""
        self.encodedImagePath = ""
        
        selectOriginalButton = tk.Button(imageFrame, text="Wybierz oryginalny obraz", command=self.selectOriginalImage)
        selectEncodedButton = tk.Button(imageFrame, text="Wybierz zakodowany obraz", command=self.selectEncodedImage)
        
        selectOriginalButton.grid(row=0, column=0, padx=10, pady=5)
        selectEncodedButton.grid(row=0, column=1, padx=10, pady=5)
        
        # Wyświetlanie obrazów
        self.originalImageLabel = tk.Label(imageFrame, text="Oryginalny obraz")
        self.encodedImageLabel = tk.Label(imageFrame, text="Zakodowany obraz")

        self.originalImageLabel.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.encodedImageLabel.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Wyświetlanie statystyk
        statsFrame = tk.Frame(tab)
        statsFrame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.psnrLabel = tk.Label(statsFrame, text="PSNR: N/A")
        self.mseLabel = tk.Label(statsFrame, text="MSE: N/A")
        
        self.psnrLabel.pack()
        self.mseLabel.pack()

        # Przycisk do obliczenia statystyk
        calculateStatsButton = tk.Button(tab, text="Oblicz statystyki", command=self.calculateStats)
        calculateStatsButton.grid(row=3, column=0, pady=10)

    def selectOriginalImage(self):
        filePath = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if filePath:
            self.originalImagePath = filePath
            self.displayImage(filePath, self.originalImageLabel)

    def selectEncodedImage(self):
        filePath = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if filePath:
            self.encodedImagePath = filePath
            self.displayImage(filePath, self.encodedImageLabel)

    def displayImage(self, filePath, label):
        image = Image.open(filePath)
        image.thumbnail((200, 200))  # Zmniejszenie rozmiaru obrazu do wyświetlenia
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo, text="")  # Usunięcie tekstu
        label.image = photo

    def calculateStats(self):
        if not self.originalImagePath or not self.encodedImagePath:
            self.showTextInWindow("Wybierz oba obrazy przed obliczeniem statystyk.")
            return

        # Wczytaj obrazy do tablic numpy
        original = cv2.imread(self.originalImagePath)
        encoded = cv2.imread(self.encodedImagePath)

        if original.shape != encoded.shape:
            self.showTextInWindow("Obrazy muszą mieć ten sam rozmiar.")
            return

        # Oblicz MSE
        mse = np.mean((original - encoded) ** 2)
        self.mseLabel.config(text=f"MSE: {mse:.2f}")

        # Oblicz PSNR
        if mse == 0:
            psnr = float('inf')
        else:
            psnr = 20 * np.log10(255.0 / np.sqrt(mse))
        self.psnrLabel.config(text=f"PSNR: {psnr:.2f} dB")

    def showTextInWindow(self, text):
        # Create a new Toplevel window
        newWindow = tk.Toplevel()
        newWindow.title("Text Display")
        
        # Create a label to show the text
        textLabel = tk.Label(newWindow, text=text, wraplength=300, justify="left")
        textLabel.pack(padx=20, pady=20)

        # Add a close button
        closeButton = tk.Button(newWindow, text="Zamknij", command=newWindow.destroy)
        closeButton.pack(pady=5)

    def encode(self, tabsName):
        # Get the text from the text entry box for the specific tab
        text = self.textEntries[tabsName].get("1.0", tk.END).strip()
        imagePath = self.imagePaths[tabsName]  # Get the selected image path for this tab

        if not imagePath:
            self.showTextInWindow("Musisz wybrać zdjęcie")
            print("Musisz wybrać zdjęcie")  # Prompt to select an image
            return

        if text:
            match tabsName:
                case "LSB":
                    lsbRGB.encode(imagePath, text)
                case "FiveModulus":
                    fm.encode(imagePath, text) 
                case "EdgeLSB":
                    lsbE.encode(imagePath,text)
                case "PVD":
                    pvd.encode(imagePath,text)
            print(f"Encoding text in {tabsName} tab: {text}")
            print(imagePath.split("/")[-1].split(".")[0])
        else:
            self.showTextInWindow("Wpisz tekst do zakodowania")
            print("No text entered for encoding")

    def decode(self, tabsName):
        imagePath = self.imagePaths[tabsName]  # Get the selected image path for this tab

        if not imagePath:
            self.showTextInWindow("Musisz wybrać zdjęcie")
            print("Musisz wybrać zdjęcie")  # Prompt to select an image
            return

        result = ""
        try:
            match tabsName:
                case "LSB":
                    result = lsbRGB.decode(imagePath)
                case "FiveModulus":
                    result = fm.decode(imagePath) 
                case "EdgeLSB":
                    result = lsbE.decode(imagePath)
                case "PVD":
                    result = pvd.decode(imagePath)
            self.showTextInWindow(f"Zakodowana wiadomośc to:\n{result}")
            print("Zakodowana wiadomość to: ", result)
        except:
            self.showTextInWindow("W zdjęciu nie ma zakodowanej wiadomości")

    def selectImage(self, tabsName):
        # Function to select an image file for the specific tab
        filePath = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if filePath:
            print(f"Selected image in {tabsName}: {filePath}")
            # Update the image path for this tab
            self.imagePaths[tabsName] = filePath
            # Update the label to show the selected image's path
            self.imagePathLabels[tabsName].config(text=f"Wybrane zdjęcie: {filePath.split('/')[-1]}")  # Display the selected image path

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()


#   import tkinter as tk
#   import LSBInEdges as lsbE
#   import fiveModulus as fm
#   import lsbRGB as lsbRGB
#   import PVD as pvd
#   from tkinter import ttk, filedialog

#   class App:
#       def __init__(self, root):
#           self.root = root
#           self.root.title("Steganografia")

#           self.root.rowconfigure(0, weight=1)
#           self.root.columnconfigure(0, weight=1)

#           self.notebook = ttk.Notebook(self.root)
#           self.notebook.grid(sticky="nsew", padx=10, pady=10)

#           # Creating tabs
#           self.tabs = []
#           self.textEntries = {}  # Dictionary to hold text entries for each tab
#           self.imagePaths = {}    # Dictionary to hold selected image paths for each tab
#           self.imagePathLabels = {}  # Dictionary to hold labels for image paths
#           tabsName = ["LSB", "FiveModulus", "EdgeLSB", "PVD", "COS", "COS", "COS"]
#           for i in range(7):
#               tab = ttk.Frame(self.notebook)
#               self.notebook.add(tab, text=tabsName[i])
#               self.tabs.append(tab)
#               self.createTab(tab, tabsName[i])

#       def createTab(self, tab, tabsName):
#           # Configure grid weights to make elements inside the tab responsive
#           tab.rowconfigure(1, weight=1)
#           tab.columnconfigure(0, weight=1)

#           # Encoding and decoding buttons (at the top)
#           buttonFrame = tk.Frame(tab)
#           buttonFrame.grid(row=0, column=0, pady=10, sticky="ew")
#           buttonFrame.columnconfigure(0, weight=1)
#           buttonFrame.columnconfigure(1, weight=1)
#           buttonFrame.columnconfigure(2, weight=0)  # For the Info button

#           encodeButton = tk.Button(buttonFrame, text="Kodowanie", width=20, command=lambda: self.encode(tabsName))
#           decodeButton = tk.Button(buttonFrame, text="Dekodowanie", width=20, command=lambda: self.decode(tabsName))
#           
#           # Move the info button to the middle
#           infoButton = tk.Button(buttonFrame, text="Info", command=lambda: self.showInfo())

#           encodeButton.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
#           infoButton.grid(row=0, column=1, padx=20, pady=5, sticky="ew")  # Place it between Kodowanie and Dekodowanie
#           decodeButton.grid(row=0, column=2, padx=20, pady=5, sticky="ew")

#           # Containers for text input and image selection
#           mainFrame = tk.Frame(tab)
#           mainFrame.grid(row=1, column=0, pady=10, sticky="nsew")
#           mainFrame.columnconfigure(0, weight=1)
#           mainFrame.columnconfigure(1, weight=3)

#           # Text entry field for encoding (specific to this tab)
#           textEntry = tk.Text(mainFrame, height=5, width=40)
#           textEntry.grid(row=0, column=1, padx=20, sticky="nsew")
#           self.textEntries[tabsName] = textEntry  # Store the text entry for this tab

#           # Button to select image
#           selectImageButton = tk.Button(tab, text="Wybierz zdjęcie", command=lambda: self.selectImage(tabsName))
#           selectImageButton.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

#           # Label to show the selected image's path (specific to this tab)
#           imagePathLabel = tk.Label(tab, text="", fg="blue")
#           imagePathLabel.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
#           self.imagePathLabels[tabsName] = imagePathLabel  # Store the label for this tab

#           # Initialize image path for this tab
#           self.imagePaths[tabsName] = ""  # Store the image path for this tab

#       def showInfo(self):
#           # Create a new Toplevel window for the info
#           infoWindow = tk.Toplevel(self.root)
#           infoWindow.title("Informacje")
#           
#           # Create a label with information text
#           infoText = tk.Label(infoWindow, text="This is an application for steganography.\n\n"
#                                               "Use the buttons to encode or decode messages in images.\n"
#                                               "Select an image using 'Wybierz zdjęcie' button.")
#           infoText.pack(padx=20, pady=20)

#           # Add a close button
#           closeButton = tk.Button(infoWindow, text="Close", command=infoWindow.destroy)
#           closeButton.pack(pady=5)

#       def showTextInWindow(self, text):
#           # Create a new Toplevel window
#           newWindow = tk.Toplevel()
#           newWindow.title("Text Display")
#           
#           # Create a label to show the text
#           textLabel = tk.Label(newWindow, text=text, wraplength=300, justify="left")
#           textLabel.pack(padx=20, pady=20)

#           # Add a close button
#           closeButton = tk.Button(newWindow, text="Zamknij", command=newWindow.destroy)
#           closeButton.pack(pady=5)


#   if __name__ == "__main__":
#       root = tk.Tk()
#       app = App(root)

#       # Set the window to be resizable
#       root.rowconfigure(0, weight=1)
#       root.columnconfigure(0, weight=1)
#       root.mainloop()
