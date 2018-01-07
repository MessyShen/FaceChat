import cv2
import numpy as np

def beautyFace(img):
    dst = np.zeros_like(img)
    v1 = 3
    v2 = 1
    dx = v1 * 5
    fc = v1 * 12.5
    p = 0.1

    temp4 = np.zeros_like(img)

    temp1 = cv2.bilateralFilter(img, dx, fc, fc)
    temp2 = cv2.subtract(temp1, img);
    temp2 = cv2.add(temp2, (10, 10, 10, 128))
    temp3 = cv2.GaussianBlur(temp2,(2*v2-1, 2*v2-1),0)
    temp4 = cv2.add(img, temp3)
    dst = cv2.addWeighted(img, p, temp4, 1-p, 0.0)
    dst = cv2.add(dst, (10, 10, 10, 255))
    return dst
