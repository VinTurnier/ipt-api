# Standard Application Imports
import re
import requests
import datetime
import json
import logging
import subprocess
import time

# Third Party Imports
from skimage.measure import compare_ssim
import cv2
import numpy as np
import boto3
from botocore.exceptions import ClientError


# IPT Models Imports
from ipt.db import Image
from ipt.db import session


class KeyPointDescriptorEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, cv2.KeyPoint):
            return serialize_key_point(obj)
        elif isinstance(obj,np.ndarray):
            return serialize_descriptor(obj)
        return json.JSONEncoder.default(self, obj)

def serialize_key_point(keypoint):
    ''' Turns keypoint object to a dictianory

    :params keypoint: cv2.Keypoint object
    :return: keypoint_dictionary
    '''
    keypoint_dictionary = {
        "__class__": "KeyPoints",
        "pt": keypoint.pt,
        "size":keypoint.size,
        "angle":keypoint.angle,
        "response": keypoint.response,
        "octave": keypoint.octave,
        "class_id": keypoint.class_id,
    }
    return keypoint_dictionary


def deserialize_key_point(keypoint):
    ''' Turns a dictionary of key points to a keypoint objects

    :params keypoint: a dictionary of keypoints
    :return: keypoint object

    '''
    _keypoint = cv2.KeyPoint(x=keypoint['pt'][0],y=keypoint['pt'][1],_size=keypoint['size'], _angle=keypoint['angle'], 
                            _response=keypoint['response'], _octave=keypoint['octave'], _class_id=keypoint['class_id'])
    return _keypoint

def serialize_descriptor(descriptor):
    ''' Turns descript 2d numpy array to a list

    :params descriptor: takes in a descriptor numpy 2d array
    :return: a descriptor dictionary with the 2d array as a list
    '''
    list_descriptor = descriptor.tolist()
    return list_descriptor

def deserialize_descriptor(descriptor):
    ''' Turns a descriptor dictionary to a numpy 2d array

    :params descriptor: a dictionary descriptor with a 2d array a value
    :return: a numpy 2d array
    '''
    _descriptor = np.array(descriptor)
    return _descriptor

def file_name(bucket_name,length,timestamp):
    ''' Creates a file name given a bucket_name, length and timestamp

    :param bucket_name: key_point, or descriptor will be prefixed to the fi
    :param length: the lenght of the array object
    :param timestamp: the time at which this file was created
    :return: file_name
    '''
    filename = f"{bucket_name}_{length}_{timestamp}.json"
    return filename

def write_json_file(bucket_name,data):
    ''' Populates .obj file using python pickel module

    :param filename: name of file to write to
    :param data: the data that will be stored in the file
    :return: filename 
    '''
    length = len(data['keypoints'])
    now = datetime.datetime.now()
    timestamp = now.strftime("%m%d%Y%H%M%S")
    filename = file_name(bucket_name,length,timestamp)
    with open(filename,'w') as fp:
        json.dump(data,fp,cls=KeyPointDescriptorEncoder)

    return filename 

def read_json_file(filename):
    ''' Read keypoints_descriptor json file and deserializes keypoints and descriptor

    :params filename: s3 file name
    :returns: keypoints, and descriptor
    '''

    with open(filename) as json_file:
        data = json.load(json_file)
        keypoints = []
        for p in data['keypoints']:
            keypoints.append(deserialize_key_point(p))
        descriptor = deserialize_descriptor(data['descriptor'])
        return keypoints, descriptor

def get_keypoints_length(filename):
    ''' Takes the file name and return the length of the keypoints

    :params filename: name of file from database
    :return: length of keypoints which is found in the file name
    '''
    filename_split = filename.split('_')
    length = filename_split[2]
    return length

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, 'keypoints_descriptor/'+file_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def read_from_s3_ipt_bucket(bucket_name,file_path):
    ''' Read file directly from S3 bucket without downloading

    :param bucket_name: the bucket to read from
    :param file_path: the S3 key to read from
    :return: json load data that is read from S3
    '''
    
    client = boto3.client('s3')
    obj = client.get_object(Bucket=bucket_name, Key=file_path)
    return json.load(obj['Body'])


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
    start = time.time()
    # imageA = url_to_image('https://api.twilio.com/2010-04-01/Accounts/ACfcd00e1e9a29eab742a84b432485fe39/Messages/MM135aec9a461670d3e45aa9e7e8f8550d/Media/MEfe4c23bdee6b45c6cf36827cb345fd99')
    imageA = url_to_image('https://api.twilio.com/2010-04-01/Accounts/ACfcd00e1e9a29eab742a84b432485fe39/Messages/MM7194f3f4c29ca71cd6fa005f8afa976f/Media/MEdb0e5d2a44745462dd7125c7e5e60289')
    orb = cv2.ORB_create()
    kp_1, des1 = orb.detectAndCompute(imageA, None)
    elapsed_time_fl = (time.time() - start)
    print("Key Point & Descriptor time: "+str(elapsed_time_fl))
    data = {
        "keypoints": kp_1,
        "descriptor": des1
    }
    start = time.time()
    filename = write_json_file("keypoints_descriptors",data)
    upload_file(filename,'ipt-staging')
    subprocess.call(f"rm {filename}",shell=True)
    elapsed_time_fl = (time.time() - start)
    print("Upload to S3: "+str(elapsed_time_fl))
    start = time.time()
    data = read_from_s3_ipt_bucket('ipt-staging','keypoints_descriptor/keypoints_descriptors_500_12012019174936.json')
    elapsed_time_fl = (time.time() - start)
    print("Download from S3: "+str(elapsed_time_fl))
    # read_json_file('ipt_key_points_2_12012019163238.json')
