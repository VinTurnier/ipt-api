from ipt.db.images import Image
from ipt.db.base import session

from skimage.measure import compare_ssim
# import argparse
import cv2
import requests
import numpy as np
import re

def is_url(url):
    ''' Checks to see if string is a url'''
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url) 
    if url:
        return True
    else:
        return False
    

def url_to_image(url):
    resp = requests.get(url)
    image = np.asarray(bytearray(resp.content), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

def ssim_comparison(imageA,imageB):
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # 5. Compute the Structural Similarity Index (SSIM) between the two
    #    images, ensuring that the difference image is returned
    score, diff = compare_ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype("uint8")

    # 6. You can print only the score if you want
    return score

def sift_comparison(imageA,imageB):
    sift = cv2.xfeatures2d.SIFT_create()
    kp_1, desc_1 = sift.detectAndCompute(imageA, None)
    kp_2, desc_2 = sift.detectAndCompute(imageB, None)
    index_params = dict(algorithm=0, trees=5)
    search_params = dict()
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(desc_1, desc_2, k=2)
    good_points = []
    ratio = 0.6
    for m, n in matches:
        if m.distance < ratio*n.distance:
            good_points.append(m)
            print(len(good_points))
    
    number_keypoints = 0
    if len(kp_1) <= len(kp_2):
        number_keypoints = len(kp_1)
    else:
        number_keypoints = len(kp_2)

    result = len(good_points) / number_keypoints

    return result

def select_algo(imageA,imageB):
    if imageA is None or imageB is None:
        return 0

    if imageA.shape == imageB.shape:
        return ssim_comparison(imageA,imageB)
    else:
        return sift_comparison(imageA,imageB)

def image_in_database(url,threshold):
    images = session.query(Image).all()
    for image in images:
        if is_url(image.url):
            imageA_url = image.url
            imageA = url_to_image(imageA_url)
            imageB_url = url
            imageB = url_to_image(imageB_url)
            score = select_algo(imageA,imageB)
            if score >= threshold:
                return {
                    'statusCode':200,
                    'image_in_db':1,
                    'ssim_score':score,
                    'date_posted':image.timestamp,
                    'body': f'Image sa gen {score*100}% chanse li te poste le {image.timestamp}'
                }

    return {
            'statusCode':200,
            'image_in_db':0,
        }

    
def lambda_handler(event,context):
    image_url = event.get('url')
    threshold = event.get('threshold')
    result = image_in_database(image_url,threshold)
    return result
