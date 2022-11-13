# Python Image Steganography

This project involves using Python to implement Image Steganography, which entails creating a GUI tool that enables a user to encode a message in an image and send it to another user over a TCP connection, where the message is then decoded.

## Requirements
 - tkinter
 - opencv
 - numpy
 - PIL (Python Imaging Library)

### Steps to run:
1. Install the required libraries using ``` pip install -r requirements.txt ```
2. Run the Server using ``` python3 server.py ```
4. Run the Client using ``` python3 client.py ```
3. In the Server GUI, enter text to hide and select a PNG file to hide the data in.
5. Client GUI will automatically open once the image has been successfully received.
6. Click 'Decode' to reveal the hidden data.

*Note: Running this will create an 'EncodedImages' directory on the Client side, and a 'RcvdImages' directory on the Server side, to store the stegano images.*