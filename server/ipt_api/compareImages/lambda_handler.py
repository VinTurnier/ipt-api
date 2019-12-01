# Standard Application Imports
import re
import requests
import datetime
import pickle

# Third Party Imports
from skimage.measure import compare_ssim
import cv2
import numpy as np


# IPT Models Imports
from ipt.db import Image
from ipt.db import session

def serializing_key_point(keypoint):
    pass

def deserializing_key_point(keypoint):
    pass

def serializing_descriptor(descriptor):
    pass

def deserializing_descriptor(descriptor):
    pass

def file_name(bucket_name,length,timestamp):
    ''' Creates a file name given a bucket_name, length and timestamp

    :param bucket_name: key_point, or descriptor will be prefixed to the fi
    :param length: the lenght of the array object
    :param timestamp: the time at which this file was created
    :return: file_name
    '''
    filename = f"{bucket_name}_{length}_{timestamp}.obj"
    return filename

def make_obj_file(bucket_name,data):
    ''' Populates .obj file using python pickel module

    :param filename: name of file to write to
    :param data: the data that will be stored in the file
    :return: True if file was written successfully, else returns False
    '''
    length = len(data)
    now = datetime.datetime.now()
    timestamp = now.strftime("%m%d%Y%H%M%S")
    filename = file_name(bucket_name,length,timestamp)
    with open(filename,'wb') as fp:
        for value in data:
            pickle.dump(value,fp)
    pass 


def get_key_points_and_descriptors(Image):
    '''
        Used to grab the image points and descriptors
        Parameter: Image -> an Image object
        Returns: kp_1 -> key points of the image
                 des1 -> descriptor of that image
    '''
    orb = cv2.ORB_create()
    kp_1, des1 = orb.detectAndCompute(image, None)
    return kp_1, des1


def is_url(url):
    ''' 
        Checks to see if string is a url
    '''
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url) 
    if url:
        return True
    else:
        return False
    

def url_to_image(url):
    '''
        Turns a URL link image into an image, basically downloads the image from the internet
        input: url string
        return: image
    '''
    resp = requests.get(url)
    image = np.asarray(bytearray(resp.content), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

def ssim_comparison(imageA,imageB):
    '''
    Structural SIMularity index or SSIM is a method used to compare simularities between two images.
    is it used to measure the quality of an image.
    Parameters: ImageA, ImageB
            Takes in the two images that will be compared
    Return: score
            Which is the comparison score between 0 and 1 that returns from compare_ssim
    '''
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    score, diff = compare_ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype("uint8")

    return score

def sift_comparison(imageA,imageB):
    '''
    Scale Inveriant Feature Transform or SIFT is an image comparison algorithm that is currently patented,
    and cannot be used in production. It is a feature detection algorithm in computer vision to detect and describe
    local features in images. https://en.wikipedia.org/wiki/Scale-invariant_feature_transform
    Parameters: imageA, imageB
        Takes in the two images that will be used to make a comparison
    return: score
        Score is the a number between 0 and 1 that represents the similarity between the two images.
    '''
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
    
    number_keypoints = 0
    if len(kp_1) <= len(kp_2):
        number_keypoints = len(kp_1)
    else:
        number_keypoints = len(kp_2)

    score = len(good_points) / number_keypoints

    return score

def orb_comparison(imageA,imageB):
    '''
    Link: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_orb/py_orb.html
    Oriented FAST and Rotated BRIEF or ORB ORB is basically a fusion of FAST keypoint 
    detector and BRIEF descriptor with many modifications to enhance the performance
    Parameters: imageA, imageB
        Takes in the two images that will be compared
    return: score
        Score is the a number between 0 and 1 that represents the similarity between the two images.
    '''
    orb = cv2.ORB_create()
    kp_1, des1 = orb.detectAndCompute(imageA, None) 
    kp_2, des2 = orb.detectAndCompute(imageB, None)

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2,k=2)

    good_matches = []
    ratio = 0.75
    for m, n in matches:
        if m.distance < ratio*n.distance: 
            good_matches.append([m])
    
    number_keypoints = 0

    if len(kp_1) <= len(kp_2):
        number_keypoints = len(kp_1)
    else:
        number_keypoints = len(kp_2)

    score = len(good_matches) / number_keypoints

    return score

def compare(url,threshold):
    '''
        Compares the image that is received from whatsapp to those in the database
        Parameters: url -> the url that is sent by whatsapp
                    threshold -> the accepted threshold that has to be met for the comparison the return that the image
                                is in the database
        Return: if threshold is reached a dictionary with a 
                                few keys -> statusCode: 200 means it received the data properly
                                            image_in_db: 1 means that the image we are processing is actually in the dictionary
                                            score: the value between 0 and 1 that was reached by comparing images
                                            date_posted: the date that the image was in the database
                                            body: the message that will be sent back to the end user
                else  a dictionary with a few keys ->
                                            statusCode: 200 marked as transaction completed
                                            image_in_db: 0 means that the image was not found in the database base on the threshold
    '''
    images = session.query(Image).all()
    for image in images:
        if is_url(image.url):
            imageA_url = image.url
            imageA = url_to_image(imageA_url)
            imageB_url = url
            imageB = url_to_image(imageB_url)
            score = orb_comparison(imageA,imageB)
            if score >= threshold:
                return {
                    'statusCode':200,
                    'image_in_db':1,
                    'score':score,
                    'image_id':image.id,
                    'date_posted':image.timestamp,
                    'body': 'This image has {0}% possibility that it was posted on {1}'.format(score*100,image.timestamp)
                }

    return {
            'statusCode':200,
            'image_in_db':0,
        }

    
def lambda_handler(event,context):
    '''
        Parameters: event -> the event that is sent to the endpoint
                    context -> used for aws to specify lambda configuration in code
        Return: results found in the compare method which is a dictionary
    '''
    image_url = event.get('url')
    threshold = event.get('threshold')
    result = compare(image_url,threshold)
    return result


if __name__=="__main__":
    imageA = url_to_image('https://api.twilio.com/2010-04-01/Accounts/ACfcd00e1e9a29eab742a84b432485fe39/Messages/MM135aec9a461670d3e45aa9e7e8f8550d/Media/MEfe4c23bdee6b45c6cf36827cb345fd99')
    imageB = url_to_image('https://api.twilio.com/2010-04-01/Accounts/ACfcd00e1e9a29eab742a84b432485fe39/Messages/MM7194f3f4c29ca71cd6fa005f8afa976f/Media/MEdb0e5d2a44745462dd7125c7e5e60289')
    orb = cv2.ORB_create()
    kp_1, des1 = orb.detectAndCompute(imageA, None)
    make_obj_file("key_points",kp_1)

