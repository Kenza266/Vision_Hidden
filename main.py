import streamlit as st  
import numpy as np
import cv2

def char_generator(message, option):
    for c in message:
        if option == 'RGBA':
            yield ord(c)
        elif option == 'YCbCr':
            yield c

def modifyBit(n, p, b):
    mask = 1 << p
    return (n & ~mask) | ((b << p) & mask)

def encode_message(message):
    message_b = [np.binary_repr(int(ord(m)), width=8) for m in message]
    message_b = [m[i:i+2] for m in message_b for i in range(0, len(m), 2)]
    message_b = [int(i) for i in message_b]
    return message_b

def decode_message(message):
    message = [np.binary_repr(m, width=2) if m == 0 or m == 1 else str(m) for m in message]
    message = [chr(int(''.join(message[i:i+4]), 2)) for i in range(0, len(message), 4)]
    return ''.join(message)

def load_image(image_file):
    bytes_data = image_file.getvalue()
    nparr = np.frombuffer(bytes_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR).astype(np.uint16)
    return img

def encode_pixel(byte, pixel, option):
    if option == 'RGBA':
        r = (byte&3)
        g = (byte&12)>>2
        b = (byte&48)>>4
        a = (byte&192)>>6

        return (r+(pixel[0]&252),\
                g+(pixel[1]&252),\
                b+(pixel[2]&252),\
                a+(pixel[3]&252))
    elif option == 'YCbCr':
        pixel = modifyBit(pixel, 0, 1)
        pixel = modifyBit(pixel, 1, 1)
        pixel = modifyBit(pixel, 2, 1)
        pixel = modifyBit(pixel, 3, 0)
        return (byte<<4)+(pixel&65487)

def decode_from_pixel(pixel, option):
    if option == 'RGBA':
        r = pixel[0]&3
        g = pixel[1]&3
        b = pixel[2]&3
        a = pixel[3]&3
        return chr(r + (g<<2) + (b<<4) + (a<<6))
    elif option == 'YCbCr':
        return int(np.binary_repr((pixel&48)>>4))

def encode(image, message, option):
    encoded_image = image.copy()
    if option == 'RGBA':
        message = char_generator(message, option)
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                try:
                    encoded_image[i][j] = encode_pixel(next(message), image[i][j], option)
                except StopIteration:
                    encoded_image[i][j] = [0, 0, 0, 0]
                    return encoded_image, cv2.cvtColor(encoded_image, cv2.COLOR_RGBA2RGB)
    elif option == 'YCbCr':
        message = encode_message(message)
        message = char_generator(message, option)
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                try:
                    encoded_image[i][j][1] = encode_pixel(next(message), image[i][j][1], option)
                except StopIteration:
                    encoded_image[i][j][1] = 0
                    return encoded_image, cv2.cvtColor(encoded_image, cv2.COLOR_YCR_CB2RGB)

def decode(image, option):
    if option == 'RGBA':
        message = ''
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if(all(image[i][j]) == all([0, 0, 0, 0])):
                    return message
                message += decode_from_pixel(image[i][j], option)
    elif option == 'YCbCr':
        message = []
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if(image[i][j][1] == 0):
                    return decode_message(message)
                message.append(decode_from_pixel(image[i][j][1], option))


st.set_page_config(layout='wide')
st.title('Hidden Message')

try:
    image = st.file_uploader('Choose an image')
    message = st.text_input('Message')
    file_details = {'filename': image.name}
    image = load_image(image)
except:
    image = cv2.imread('Test_Image.jpg').astype(np.uint16)
    message = 'Test message'

image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

option = st.selectbox(
    'Please choose the encoding technique',
    ('RGBA', 'YCbCr'))

og_img_col, slider_col, new_img_col = st.columns([2, 1, 2])

with og_img_col:
    st.write('Choosen image')
    st.image(image.astype(np.uint8), caption='Shape: '+str(image.shape)+', type:'+str(image.dtype)) # channels, output_format
    st.write('Message: ' + message)

with slider_col:
    slider = st.select_slider('Send', options=['Sender', 'Receiver'], label_visibility='hidden')

if option == 'RGBA':
    image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA).astype(np.uint16)
elif option == 'YCbCr':
    image = cv2.cvtColor(image, cv2.COLOR_RGB2YCR_CB).astype(np.uint16)

if slider == 'Receiver' and image is not None and message != '':
    new_img, enc_message = encode(image, message, option)
    with new_img_col:
        st.write('Image containing the message')
        st.image(enc_message.astype(np.uint8), caption='Shape: '+str(enc_message.shape)+', type:'+str(enc_message.dtype)) 
        decoded_message = decode(new_img, option)
        st.write('Decoded message: ' + decoded_message)
        