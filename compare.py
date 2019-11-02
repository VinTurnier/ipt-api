import cv2
import numpy as np
import requests

def drawMatches(img1, kp1, img2, kp2, matches):

    rows1 = img1.shape[0]
    cols1 = img1.shape[1]
    rows2 = img2.shape[0]
    cols2 = img2.shape[1]

    out = np.zeros((max([rows1,rows2]),cols1+cols2,3), dtype='uint8')
    out[:rows1,:cols1] = np.dstack([img1])
    out[:rows2,cols1:] = np.dstack([img2])
    for mat in matches:
        img1_idx = mat.queryIdx
        img2_idx = mat.trainIdx
        (x1,y1) = kp1[img1_idx].pt
        (x2,y2) = kp2[img2_idx].pt

        cv2.circle(out, (int(x1),int(y1)), 4, (255, 0, 0, 1), 1)   
        cv2.circle(out, (int(x2)+cols1,int(y2)), 4, (255, 0, 0, 1), 1)
        cv2.line(out, (int(x1),int(y1)), (int(x2)+cols1,int(y2)), (255, 0, 0, 1), 1)

    return out

def compare(img1, img2):

    # Initiate SIFT detector
    sift = cv2.xfeatures2d.SIFT_create()

    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)

    # BFMatcher with default params
    bf = cv2.BFMatcher()
    matches = bf.match(des1,des2)

    matches = sorted(matches, key=lambda val: val.distance)

    img3 = drawMatches(img1,kp1,img2,kp2,matches[:25])

    # Show the image
    cv2.imshow('Matched Features', img3)
    cv2.waitKey(0)
    cv2.destroyWindow('Matched Features')

def url_to_img(url):
    resp = requests.get(url)
    image = np.asarray(bytearray(resp.content), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

if __name__=='__main__':
    img1 = url_to_img('https://api.twilio.com/2010-04-01/Accounts/ACfcd00e1e9a29eab742a84b432485fe39/Messages/MMdddd999ba7f09910264497165f0e9ce6/Media/MEa31d49d083a5ff01c0badb4194382a62')
    img2 = url_to_img('https://api.twilio.com/2010-04-01/Accounts/ACfcd00e1e9a29eab742a84b432485fe39/Messages/MMdcbf58eabeea81791d0d98d5233e749e/Media/MEf44bbfbe7ec7d08195dd9a9f320459a2')
    compare(img1,img2)
