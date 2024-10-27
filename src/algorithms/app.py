import tkinter as tk
from tkinter import ttk, filedialog

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikacja Kodowanie/Dekodowanie")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(sticky="nsew", padx=10, pady=10)

        # Creating tabs
        self.tabs = []
        tabsName = ["LSB", "FiveModulus", "EdgeLSB", "COS", "COS", "COS", "COS"]
        for i in range(7):
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=tabsName[i])
            self.tabs.append(tab)
            self.create_tab(tab)

        # Button at the bottom to select an image from the filesystem
        self.select_image_button = tk.Button(self.root, text="Select Image", command=self.select_image)
        self.select_image_button.grid(row=1, column=0, pady=10, padx=10, sticky="ew")

    def create_tab(self, tab):
        # Configure grid weights to make elements inside the tab responsive
        tab.rowconfigure(1, weight=1)
        tab.columnconfigure(0, weight=1)

        # Encoding and decoding buttons (at the top)
        button_frame = tk.Frame(tab)
        button_frame.grid(row=0, column=0, pady=10, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        encode_button = tk.Button(button_frame, text="Kodowanie", width=20, command=lambda: self.encode(tab))
        decode_button = tk.Button(button_frame, text="Dekodowanie", width=20, command=lambda: self.decode(tab))

        encode_button.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
        decode_button.grid(row=0, column=1, padx=20, pady=5, sticky="ew")

        # Containers for text input/file selection options and input fields
        main_frame = tk.Frame(tab)
        main_frame.grid(row=1, column=0, pady=10, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)

        # Option to input text or select a file (on the left)
        option_frame = tk.Frame(main_frame)
        option_frame.grid(row=0, column=0, padx=20, sticky="nw")

        self.text_option = tk.StringVar(value="text")
        text_radio = tk.Radiobutton(option_frame, text="Wpisz tekst", variable=self.text_option, value="text", command=self.toggle_input)
        file_radio = tk.Radiobutton(option_frame, text="Wybierz plik", variable=self.text_option, value="file", command=self.toggle_input)
        text_radio.pack(anchor="w")
        file_radio.pack(anchor="w")

        # Input fields (on the right)
        self.input_frame = tk.Frame(main_frame)
        self.input_frame.grid(row=0, column=1, padx=20, sticky="nsew")

        # Text entry field
        self.text_entry = tk.Text(self.input_frame, height=5, width=40)
        self.text_entry.pack(fill=tk.BOTH, expand=True, pady=10)

        # File selection button (not shown initially)
        self.file_button = tk.Button(self.input_frame, text="Wybierz plik", command=self.load_file)

        # Initial visibility setting
        self.toggle_input()

    def toggle_input(self):
        # If the text option is selected, show the text field, hide the file button
        if self.text_option.get() == "text":
            self.text_entry.pack(fill=tk.BOTH, expand=True, pady=10)
            self.file_button.pack_forget()  # Hide the file button
        # If the file option is selected, show the file button, hide the text field
        else:
            self.text_entry.pack_forget()  # Hide the text entry
            self.file_button.pack(fill=tk.BOTH, expand=True, pady=10)

    def encode(self, tab):
        if self.text_option.get() == "text":
            text = self.text_entry.get("1.0", tk.END).strip()
            print(f"Encoding text: {text}")
        else:
            print("Encoding file")

    def decode(self, tab):
        if self.text_option.get() == "text":
            text = self.text_entry.get("1.0", tk.END).strip()
            print(f"Decoding text: {text}")
        else:
            print("Decoding file")

    def load_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                self.text_entry.delete("1.0", tk.END)
                self.text_entry.insert(tk.END, content)

    def select_image(self):
        # Function to select an image file from the filesystem
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            print(f"Selected image: {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    # Set the window to be resizable
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.mainloop()
