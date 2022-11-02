import streamlit as st  
import numpy as np
import cv2


def char_generator(message, type):
    for c in message:
        if type == 'RGBA':
            yield ord(c)
        elif type == 'YCbCr':
            yield c

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

def encode_pixel(byte, pixel, type):
    if type == 'RGBA':
        r = (byte&3)
        g = (byte&12)>>2
        b = (byte&48)>>4
        a = (byte&192)>>6

        return (r+(pixel[0]&252),\
                g+(pixel[1]&252),\
                b+(pixel[2]&252),\
                a+(pixel[3]&252))
    elif type == 'YCbCr':
        return (byte<<4)+(pixel&199)

def decode_from_pixel(pixel, type):
    if type == 'RGBA':
        r = pixel[0]&3
        g = pixel[1]&3
        b = pixel[2]&3
        a = pixel[3]&3
        return chr(r + (g<<2) + (b<<4) + (a<<6))
    elif type == 'YCbCr':
        return int(np.binary_repr((pixel&48)>>4))

def encode(image, message, type):
    encoded_image = image.copy()
    if type == 'RGBA':
        message = char_generator(message, type)
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                try:
                    encoded_image[i][j] = encode_pixel(next(message), image[i][j], type)
                except StopIteration:
                    encoded_image[i][j] = [0, 0, 0, 0]
                    return encoded_image, np.zeros_like(image)
    elif type == 'YCbCr':
        message = encode_message(message)
        message = char_generator(message, type)
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                try:
                    encoded_image[i][j][1] = encode_pixel(next(message), image[i][j][1], type)
                except StopIteration:
                    encoded_image[i][j][1] = 0
                    return encoded_image, np.zeros_like(image)
    

def decode(image, type):
    if type == 'RGBA':
        message = ''
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if(all(image[i][j]) == all([0, 0, 0, 0])):
                    return message
                message += decode_from_pixel(image[i][j], type)
    elif type == 'YCbCr':
        message = []
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if(image[i][j][1] == 0):
                    return decode_message(message)
                message.append(decode_from_pixel(image[i][j][1], type))

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

type = st.selectbox(
    'Please choose the encoding technique',
    ('RGBA', 'YCbCr'))

if type == 'RGBA':
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA).astype(np.uint16)
elif type == 'YCbCr':
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YCR_CB).astype(np.uint16)

og_img_col, slider_col, new_img_col = st.columns([2, 1, 2])

with og_img_col:
    st.write('Choosen image')
    st.image(image.astype(np.uint8), caption='Shape: '+str(image.shape)+', type:'+str(image.dtype)) # channels, output_format
    st.write('Message: ' + message)

with slider_col:
    slider = st.select_slider('Send', options=['Sender', 'Receiver'], label_visibility='hidden')

if slider == 'Receiver' and image is not None and message != '':
    new_img, enc_message = encode(image, message, type)
    with new_img_col:
        st.write('Image containing the message')
        st.image(new_img.astype(np.uint8), caption='Shape: '+str(new_img.shape)+', type:'+str(new_img.dtype)) 
        decoded_message = decode(new_img, type)
        st.write('Decoded message: ' + decoded_message)
        with st.expander('Encoded message'):
            st.image(enc_message.astype(np.uint8)) 
        