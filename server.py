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

def showData(image):
    """Reveals the data hidden in the image"""

    binaryData = ""

    for values in image:
        for pixel in values:
            r, g, b = convertToBinary(pixel)
            binaryData += r[-1]
            binaryData += g[-1]
            binaryData += b[-1]

    # Split the binary string by 8 bits
    allBytes = [binaryData[i: i+8] for i in range(0, len(binaryData), 8)]

    # Convert from bits to characters
    decodedMessage = ""
    for byte in allBytes:
        decodedMessage += chr(int(byte, 2))
        if decodedMessage[-5:] == DELIMITER:
            break
    
    return decodedMessage[:-5]

def decode_text():
    """Decodes the text present in the image"""
    image = cv2.imread(newFileName)
    text = showData(image)
    
    return text

def gotoDecodeScreen():
    """GUI that enables user to decode the text in the image"""
    
    root.destroy()
    
    decodeScreen = tk.Tk()
    decodeScreen.title("Decode")
    decodeScreen.geometry("600x600+200+200")
    decodeScreen.config(bg="#9ADBE5")

    displayLabel = tk.Label(text="Decoded Message:",bg="#9ADBE5", font=('Arial', 16), width=200)
    displayLabel.place(relx=0.3, rely=0.1, anchor = tk.CENTER)
    
    confidentialMsg = decode_text()
    messageLabel = tk.Label(text=confidentialMsg, bg='#ACF4FF', font=('Arial', 16), borderwidth=2, relief="solid", wraplength=550, justify=tk.LEFT)
    messageLabel.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

    print("Message has been decoded.")

# Create TCP Connection through socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))
server.listen(1)
print("Waiting for connection...")

server_socket, server_addr = server.accept()
print("Connected to Client")

# Check if directory is present, if not then create one        
if not os.path.isdir('./RcvdImages'):
    os.mkdir('./RcvdImages')

# Receive the file name from the Client
fileName = server_socket.recv(2048).decode('utf-8')

# Receive the image from Client in bytes, 2048 byte at a time
global newFileName
newFileName = f"./RcvdImages/{fileName}.png"
imageFile = open(newFileName, "wb")
imageBytes = server_socket.recv(2048)
while imageBytes:
    imageFile.write(imageBytes)
    imageBytes = server_socket.recv(2048)

imageFile.close()
server_socket.close()

root = tk.Tk()
root.title("Image Steganography - DECODE")
root.geometry("600x500+200+200")
root.config(bg = "#ACF4FF")

textLabel = tk.Label(text="Image has been received, click to decode the message.", wraplength=500, bg="#ACF4FF", font=('Arial', 16), width=200)
textLabel.place(relx=0.5, y=50, anchor = tk.CENTER)

rcvdImage = Image.open(newFileName)
resizedImage = ImageOps.contain(rcvdImage, (550, 310))
test = ImageTk.PhotoImage(resizedImage)
imageLabel = tk.Label(image=test)
imageLabel.image = test
imageLabel.place(relx=0.5, y = 250, anchor=tk.CENTER)

decodeButton = tk.Button(text="Decode", command=gotoDecodeScreen, font=('Arial', 16), height=3, width=10, fg="#840032")
decodeButton.place(relx=0.5, y=450, anchor = tk.CENTER)

root.mainloop()