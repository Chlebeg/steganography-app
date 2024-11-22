import os
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

import cv2
import numpy as np
import webview
from PIL import Image, ImageTk
from tkinterhtml import HtmlFrame

import algorithms.fiveModulus as fm
import algorithms.fiveModulusWithTwist as fmt
import algorithms.LSBBasic as lsbB
import algorithms.LSBInEdges as lsbE
import algorithms.LSBKPoints as lsbK
import algorithms.PVD as pvd
import algorithms.LSBWithGenerator as lsbG


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganografia")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(sticky="nsew", padx=10, pady=10)

        self.tabs = []
        self.textEntries = {}  
        self.imagePaths = {}    
        self.imagePathLabels = {}
        self.encodingTime = {}
        self.characterLimit = {}
        tabsName = ["BasicLSB", "EdgeLSB", "FiveModulus", "FiveModulusWithTwist", "KPointsLSB", "PVD","LSBWithGenerator" ,"Comparison"]

        for i in range(len(tabsName)):
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=tabsName[i])
            self.tabs.append(tab)
            if tabsName[i] == "Comparison":
                self.createComparisonTab(tab)
            else:
                self.createStegoTab(tab, tabsName[i])

    def createStegoTab(self, tab, tabsName):
        """
        createStegoTab - function to create Stego tabs with encode and decode functions
        """
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)

        buttonFrame = tk.Frame(tab)
        buttonFrame.grid(row=0, column=0, pady=10, sticky="ew")
        buttonFrame.columnconfigure(0, weight=1)
        buttonFrame.columnconfigure(1, weight=1)
        buttonFrame.columnconfigure(2, weight=1)

        encodeButton = tk.Button(buttonFrame, text="Kodowanie", width=15, command=lambda: self.encode(tabsName))
        decodeButton = tk.Button(buttonFrame, text="Dekodowanie", width=15, command=lambda: self.decode(tabsName))
        infoButton = tk.Button(buttonFrame, text="Info", command=lambda: self.showInfo(tabsName))

        encodeButton.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
        infoButton.grid(row=0, column=1, padx=20, pady=5, sticky="ew")
        decodeButton.grid(row=0, column=2, padx=20, pady=5, sticky="ew")

        mainFrame = tk.Frame(tab)
        mainFrame.grid(row=1, column=0, pady=10, sticky="nsew")
        mainFrame.columnconfigure(0, weight=0)
        mainFrame.rowconfigure(0, weight=1)
        mainFrame.columnconfigure(1, weight=3)

        textEntry = tk.Text(mainFrame, height=5, width=40)
        textEntry.grid(row=0, column=1, padx=20, sticky="nsew")
        self.textEntries[tabsName] = textEntry

        selectImageButton = tk.Button(tab, text="Wybierz zdjęcie", command=lambda: self.selectImage(tabsName))
        selectImageButton.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

        # Nowy przycisk "Import z pliku" poniżej "Wybierz zdjęcie"
        importButton = tk.Button(tab, text="Import z pliku", command=lambda: self.importTextFromFile(tabsName))
        importButton.grid(row=3, column=0, pady=10, padx=10, sticky="ew")

        imagePathLabel = tk.Label(tab, text="", fg="blue")
        imagePathLabel.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        encodingTime = tk.Label(tab, text="", fg="red")
        encodingTime.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        self.imagePathLabels[tabsName] = imagePathLabel
        self.encodingTime[tabsName] = encodingTime
        self.imagePaths[tabsName] = ""

        characterLimit = tk.Label(tab, text="", fg="green")
        characterLimit.grid(row=6, column=0, padx=10, pady=10, sticky="ew")
        self.characterLimit[tabsName] = characterLimit


    def importTextFromFile(self, tabsName):
        filePath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filePath:
            with open(filePath, "r", encoding="utf-8") as file:
                text = file.read()
                self.textEntries[tabsName].delete("1.0", tk.END)  # Wyczyść pole tekstowe
                self.textEntries[tabsName].insert(tk.END, text)  # Wstaw tekst do pola


    def countCharacterLimit(self, tabsName, imagePath):
        match tabsName:
            case "BasicLSB":
                specialValue = lsbB.countCharacterLimit(imagePath)
            case "EdgeLSB":
                specialValue = lsbE.countCharacterLimit(imagePath)
            case "FiveModulus":
                specialValue = fm.countCharacterLimit(imagePath) 
            case "FiveModulusWithTwist":
                specialValue = fmt.countCharacterLimit(imagePath)
            case "KPointsLSB":
                specialValue = lsbK.countCharacterLimit(imagePath)
            case "PVD":
                specialValue = pvd.countCharacterLimit(imagePath)
            case "LSBWithGenerator":
                specialValue = lsbG.countCharacterLimit(imagePath)
        self.characterLimit[tabsName].config(text=f"Możliwa ilość znaków, które można zakodować: {specialValue}")



    def showInfo(self, tabsName):
        """
        showInfo - function to show window containing info about algorithm from an HTML file
        using pywebview to render HTML content in a separate window.
        """
        print("TEST")
        # Ustal ścieżkę do pliku HTML na podstawie tabsName
        htmlFilePath = f"info/{tabsName}.html"
        htmlFilePath = os.path.abspath(htmlFilePath)

        # Sprawdź, czy plik istnieje
        if not os.path.isfile(htmlFilePath):
            self.showTextInWindow("Plik HTML nie znaleziony. Upewnij się, że plik istnieje.")
            return

        # Wywołanie pywebview bezpośrednio bez wątkowania
        webview.create_window("Informacje", htmlFilePath)

        # Zamiast uruchamiać pywebview w innym wątku, uruchommy go w głównym wątku
        webview.start()


    def createComparisonTab(self, tab):
        """
        createComparisonTab - function to create Comparision tab
        """
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)

        imageFrame = tk.Frame(tab)
        imageFrame.grid(row=0, column=0, pady=10, sticky="nsew")
        imageFrame.columnconfigure(0, weight=1)
        imageFrame.columnconfigure(1, weight=1)

        self.originalImagePath = ""
        self.encodedImagePath = ""
        selectOriginalButton = tk.Button(imageFrame, text="Wybierz oryginalny obraz", command=self.selectOriginalImage)
        selectEncodedButton = tk.Button(imageFrame, text="Wybierz zakodowany obraz", command=self.selectEncodedImage)
        
        selectOriginalButton.grid(row=0, column=0, padx=10, pady=5)
        selectEncodedButton.grid(row=0, column=1, padx=10, pady=5)
        
        self.originalImageLabel = tk.Label(imageFrame, text="Oryginalny obraz")
        self.encodedImageLabel = tk.Label(imageFrame, text="Zakodowany obraz")

        self.originalImageLabel.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.encodedImageLabel.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        statsFrame = tk.Frame(tab)
        statsFrame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.psnrLabel = tk.Label(statsFrame, text="PSNR: N/A")
        self.mseLabel = tk.Label(statsFrame, text="MSE: N/A")
        
        self.psnrLabel.pack()
        self.mseLabel.pack()

        calculateStatsButton = tk.Button(tab, text="Oblicz statystyki", command=self.calculateStats)
        calculateStatsButton.grid(row=3, column=0, pady=10)

    def selectOriginalImage(self):
        filePath = filedialog.askopenfilename(filetypes=[("Image files", "*.png")])
        if filePath:
            self.originalImagePath = filePath
            self.displayImage(filePath, self.originalImageLabel)

    def selectEncodedImage(self):
        filePath = filedialog.askopenfilename(filetypes=[("Image files", "*.png")])
        if filePath:
            self.encodedImagePath = filePath
            self.displayImage(filePath, self.encodedImageLabel)

    def displayImage(self, filePath, label):
        image = Image.open(filePath)
        image.thumbnail((500, 500))
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo, text="")
        label.image = photo

    def calculateStats(self):
        """
        calculateStats - calculates MSE and PSNR metrics between original and stegano images
        """
        if not self.originalImagePath or not self.encodedImagePath:
            self.showTextInWindow("Wybierz oba obrazy przed obliczeniem statystyk.")
            return

        original = cv2.imread(self.originalImagePath)
        encoded = cv2.imread(self.encodedImagePath)

        if original.shape != encoded.shape:
            self.showTextInWindow("Obrazy muszą mieć ten sam rozmiar.")
            return

        mse = np.mean((original - encoded) ** 2)
        self.mseLabel.config(text=f"MSE: {mse:.4f}")

        if mse == 0:
            psnr = float('inf')
        else:
            psnr = 20 * np.log10(255.0 / np.sqrt(mse))
        self.psnrLabel.config(text=f"PSNR: {psnr:.4f} dB")

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
            print("No image selected")  # Prompt to select an image
            return
        if text:
            start = time.time()
            match tabsName:
                case "BasicLSB":
                    outputName = lsbB.encode(imagePath, text)
                case "EdgeLSB":
                    outputName = lsbE.encode(imagePath,text)
                case "FiveModulus":
                    outputName = fm.encode(imagePath, text)
                case "FiveModulusWithTwist":
                    outputName = fmt.encode(imagePath,text)
                case "KPointsLSB":
                    outputName = lsbK.encode(imagePath, text, 100) #k is hardcoded for now
                case "PVD":
                    outputName = pvd.encode(imagePath,text)
                case "LSBWithGenerator":
                    outputName = lsbG.encode(imagePath,text)
            end = time.time()
            print(end-start)
            self.imagePaths[tabsName] = outputName
            self.imagePathLabels[tabsName].config(text=f"Zdjęcie zakodowane do: {Path(outputName).name}")
            self.encodingTime[tabsName].config(text=f"Zakodowano w {end-start} sekund")
            print(f"Encoding text in {tabsName} tab: {text}")
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
                case "BasicLSB":
                    result = lsbB.decode(imagePath)
                case "EdgeLSB":
                    result = lsbE.decode(imagePath)
                case "FiveModulus":
                    result = fm.decode(imagePath) 
                case "FiveModulusWithTwist":
                    result = fmt.decode(imagePath)
                case "KPointsLSB":
                    result = lsbK.decode(imagePath)
                case "PVD":
                    result = pvd.decode(imagePath)
                case "LSBWithGenerator":
                    result = lsbG.decode(imagePath)
            self.showTextInWindow(f"Zakodowana wiadomośc to:\n{result}")
            print("Encoded message: ", result)
        except:
            self.showTextInWindow("W zdjęciu nie ma zakodowanej wiadomości")

    def selectImage(self, tabsName):
        # Function to select an image file for the specific tab
        filePath = filedialog.askopenfilename(filetypes=[("Image files", "*.png")])
        if filePath:
            print(f"Selected image in {tabsName}: {filePath}")
            # Update the image path for this tab
            self.countCharacterLimit(tabsName, filePath)
            self.imagePaths[tabsName] = filePath
            # Update the label to show the selected image's path
            self.imagePathLabels[tabsName].config(text=f"Wybrane zdjęcie: {Path(filePath).name}")  # Display the selected image path

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
