import streamlit as st  
from utils import *
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
        