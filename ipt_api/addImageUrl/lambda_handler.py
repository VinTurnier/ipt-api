from ipt.db.images import Image
from ipt.db.base import session

def add_image(url):
    if url is None:
        return {
            'statusCode':400,
            'body':{
                'message':'No URL was given'
            }
        }
    image = Image(url=url)
    session.add(image)
    session.commit()
    return {
        'statusCode':200,
        'body':{
            'message':'Image url has been added to Database'
        }
    }

def lambda_handler(event,context):
    url = event.get('url',None)
    add_image_result = add_image(url)
    return add_image_result

