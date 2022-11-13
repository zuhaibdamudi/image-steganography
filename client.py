import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from PIL import ImageTk, Image, ImageOps
import cv2
import numpy as np
import os
import socket

DELIMITER = "!@#$%"

IP = "127.0.0.1"
PORT = 4455

def convertToBinary(message):
    """Converts a string to binary"""
    
    if type(message) == str:
        return ''.join([format(ord(i), "08b") for i in message])
    elif type(message) == bytes or type(message) == np.ndarray:
        return [format(i, "08b") for i in message]
    elif type(message) == int or type(message) == np.uint8:
        return format(message, "08b")
    else:
        raise TypeError("Input type not supported")

def hideData(image, confidentialMsg):
    """Hides the confidential message into the image passed as argument"""

    print("The shape of the image is: ", image.shape)

    # Calculate the maximum bytes to encode
    maxBytesAllowed = (image.shape[0] * image.shape[1] * 3) // 8
    print("Maximum bytes to encode: ", maxBytesAllowed)

    # Check if the no. of bytes to encode is less than the max bytes i the image
    if len(confidentialMsg) > maxBytesAllowed:
        raise ValueError("Not enough bytes to fit data inside the image.")

    confidentialMsg += DELIMITER

    data_index = 0

    # Convert input data to binary format
    binaryConfidentialMsg = convertToBinary(confidentialMsg)
    length = len(binaryConfidentialMsg)

    for values in image:
        for pixel in values:
            r, g, b = convertToBinary(pixel)

            # Hide the confidential data into the LSB of RED, GREEN, and BLUE pixel
            if data_index < length:
                pixel[0] = int(r[:-1] + binaryConfidentialMsg[data_index], 2)
                data_index += 1
            if data_index < length:
                pixel[1] = int(g[:-1] + binaryConfidentialMsg[data_index], 2)
                data_index += 1
            if data_index < length:
                pixel[2] = int(b[:-1] + binaryConfidentialMsg[data_index], 2)
                data_index += 1
            
            # Once data is done encoding
            if data_index >= length:
                break

    return image

def gotoEncodeScreen():
    """GUI that enables user to encode text into an image"""

    def browseFiles():
        """Allows user to select an image"""
        global fileName
        fileName = tk.StringVar()
        fileName = fd.askopenfilename(initialdir = "/Desktop", title="SelectFile", filetypes=(("png files","*png"), ("all type of files","*.*")))
        print("File Selected: ", fileName)

        fileNameLabel = tk.Label(text=fileName, font=('Arial', 16), padx=5, pady=5, bg='#ECF8DF', wraplength=500, justify=tk.LEFT)
        fileNameLabel.place(relx=0.3, rely=0.45)

    def sendToServer():
        """Allows Client to send the stegano image to the Server"""

        # Check if image has been selected
        try:
            initImage = cv2.imread(fileName)
        except NameError:
            messagebox.showinfo("Pop Up", "Image has not been selected")
            return
        
        # Check if there is a message to hide
        hiddenMessage = messageArea.get(1.0, tk.END)
        if hiddenMessage == "\n":
            messagebox.showinfo("Pop Up", "Enter text to encode")
            return

        # Hide text inside the image
        stegoImage = hideData(initImage, hiddenMessage)

        # Check if directory is present, if not then create one        
        if not os.path.isdir('./EncodedImages'):
            os.mkdir('./EncodedImages')
        
        newFileName = "./EncodedImages/" + fileName.split('/')[-1][:-4] + ".png"
        cv2.imwrite(newFileName, stegoImage)

        # Create TCP Connection through socket
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((IP, PORT))
        print("Connected to Server")

        # Send the file name to the Server
        client.send(fileName.split('/')[-1][:-4].encode())
        
        # Send the image to the Server in bytes, 2048 bytes at a time
        imageFile = open(newFileName, 'rb')
        imageBytes = imageFile.read(2048)
        while imageBytes:
            client.send(imageBytes)
            imageBytes = imageFile.read(2048)
        
        imageFile.close() 
        client.close()

        messagebox.showinfo("Pop Up", "Image has been sent to Server.")
        encodeScreen.destroy()

    root.destroy()
    
    encodeScreen = tk.Tk()
    encodeScreen.title("Encode")
    encodeScreen.geometry("750x400+200+200")
    encodeScreen.config(bg="#bee9e8")
    
    confidentialMessageLabel = tk.Label(encodeScreen, text="Enter Confidential Message:", font=('Arial', 16), bg="#bee9e8", padx=5, pady=5)
    confidentialMessageLabel.place(relx=0.05, rely=0.15)
    
    messageArea = tk.Text(encodeScreen, font=('Arial', 16), bg='#d0f4de')
    messageArea.place(relx=0.38, rely=0.1, height=120, width=400)

    browseButton = tk.Button(encodeScreen, text="Browse Images", font=('Arial', 16), command=browseFiles, padx=10, pady=10, fg='blue')
    browseButton.place(relx=0.15, rely=0.5, anchor=tk.CENTER)
    
    sendButton = tk.Button(encodeScreen, text="Send to Server", font=('Arial', 16), command=sendToServer, padx=10, pady=10, fg='red')
    sendButton.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

root = tk.Tk()
root.title("Image Steganography - ENCODE")
root.geometry("500x300+200+200")
root.config(bg= "#d0f4de")

encodeButton = tk.Button(root, text="Encode", command=gotoEncodeScreen, font=('Arial', 18), height=3, width=10, wraplength=80, fg='darkgreen', bg='#F1F2EB')
encodeButton.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

root.mainloop()