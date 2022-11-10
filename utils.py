import numpy as np
import cv2

lenx, leny = 600, 600
max_size = 30

def char_generator(message):
    for c in message:
        yield ord(c)

def text_image_generator(message):
    lines = [] 
    start = 0
    words = message.split()
    while start in range(len(words)):
        size = 0
        i = start
        while i in range(len(words)):
            if (size + len(words[i]) < max_size):
                size += len(words[i])
                i += 1
            else:
                break
        lines.append(words[start : i])
        start = i

    img = np.zeros((lenx, leny)).astype(np.uint8) 
    for line, i in zip(lines, range(len(lines))):
        cv2.putText(img, ' '.join(line), (0, 50*(i+1)), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2, cv2.LINE_AA)
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

def decode_rgba(image):
    message = []
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if(all(image[i][j]) == all([0, 0, 0, 0])):
                return np.array(message).reshape(500, 500)
            message.append(decode_from_pixel_rgba(image[i][j]))






'''def encode_pixel_ycbr(byte, pixel):
    cr = (byte&48)>>1             #xxxx xxxx xxxb b111  0011 0000
    cb = (byte&192)>>3         #xxxx xxxx xxxc c111     1100 0000
    
    return (pixel[0],\
            cr+(pixel[1]&65504) + 7,\
            cb+(pixel[2]&65504) + 7)


def decode_from_pixel_ycbr(pixel):
    cr = pixel[1]&24
    cb = pixel[2]&24

    return (cr<<4) + (cb<<6) '''

'''def encode_pixel_ycbr(byte, pixel):
    cr = (byte&128)>>4            #xxxx xxxx xxxx b111  
    
    return (pixel[0],\
            cr+(pixel[1]&65520) + 7,\
            pixel[2])


def decode_from_pixel_ycbr(pixel):
    cr = pixel[1]&8

    return (cr<<4) '''

def encode_pixel_ycbr(byte, pixel):
    cr = (byte&128)>>3            #xxxx xxxx xxxb 0111  
    
    return (pixel[0],\
            cr+(pixel[1]&65504) + 7,\
            pixel[2])


def decode_from_pixel_ycbr(pixel):
    cr = pixel[1]&16

    return (cr<<3) 


def encode_ycbr(image, message):
    encoded_image = image.copy()
    message = text_image_generator(message)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            try:
                encoded_image[i][j] = encode_pixel_ycbr(next(message), image[i][j])
            except StopIteration:
                encoded_image[i][j] = [0, 0, 0]
                return encoded_image.astype(np.uint8), cv2.cvtColor(encoded_image, cv2.COLOR_YCR_CB2RGB) 

def decode_ycbr(image):
        message = []
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if(len(message)==lenx * leny): #all(image[i][j]) == all([0, 0, 0])):
                    return np.array(message).reshape(lenx, leny)
                message.append(decode_from_pixel_ycbr(image[i][j]))




























