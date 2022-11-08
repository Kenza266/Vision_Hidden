import numpy as np
import cv2

def char_generator(message):
    for c in message:
        yield ord(c)

def text_image_generator(message):
    img = np.zeros((100,100)).astype(np.uint8)
    cv2.putText(img, message, (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2, cv2.LINE_AA)
    for i in  img.flatten():
        yield i



def encode_pixel_rgba(byte, pixel):
    r = (byte&3)
    g = (byte&12)>>2
    b = (byte&48)>>4
    a = (byte&192)>>6

    return (r+(pixel[0]&252),\
            g+(pixel[1]&252),\
            b+(pixel[2]&252),\
            a+(pixel[3]&252))

def decode_from_pixel_rgba(pixel):
    r = pixel[0]&3
    g = pixel[1]&3
    b = pixel[2]&3
    a = pixel[3]&3
    return r + (g<<2) + (b<<4) + (a<<6)


def decode_from_pixel_rgba_str(pixel):
    r = pixel[0]&3
    g = pixel[1]&3
    b = pixel[2]&3
    a = pixel[3]&3
    return chr(r + (g<<2) + (b<<4) + (a<<6))

def encode_rgba(image, message):
    encoded_image = image.copy()
    message = text_image_generator(message)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            try:
                encoded_image[i][j] = encode_pixel_rgba(next(message), image[i][j])
            except StopIteration:
                encoded_image[i][j] = [0, 0, 0, 0]
                return encoded_image, cv2.cvtColor(encoded_image, cv2.COLOR_RGBA2RGB)

def decode(image):
    message = []
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if(all(image[i][j]) == all([0, 0, 0, 0])):
                return message
            message.append(decode_from_pixel_rgba(image[i][j]))






def encode_pixel_ycbr(byte, pixel):
    cr = (byte&48)>>1             #xxxx xxxx xxxb b111
    cb = (byte&192)>>3         #xxxx xxxx xxxc c111


    return (pixel[0],\
            cr+(pixel[1]&16352) + 7,\
            cb+(pixel[2]&16352) + 7)



def decode_from_pixel_ycbr(pixel):
    cb = pixel[1]&120
    cr = pixel[2]&120

    return cb + (cr<<4) 

def decode_from_pixel_ycbr(pixel):
    cr = pixel[1]&24
    cb = pixel[2]&24

    return (cr<<4) + (cb<<6) 


def encode_ycbr(image, message):
    encoded_image = image.copy()
    message = text_image_generator(message)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            try:
                encoded_image[i][j] = encode_pixel_ycbr(next(message), image[i][j])
            except StopIteration:
                encoded_image[i][j] = [0, 0, 0]
                return encoded_image, cv2.cvtColor(encoded_image.astype(np.uint8), cv2.COLOR_YCR_CB2RGB)

def decode_ycbr(image):
        message = []
        print(image.shape[0])
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if(len(message)==10000):#all(image[i][j]) == all([0, 0, 0])):
                    return message
                test = len(message)
                message.append(decode_from_pixel_ycbr(image[i][j]))




























