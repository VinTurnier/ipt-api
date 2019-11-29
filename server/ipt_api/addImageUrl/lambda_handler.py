# IPT Models Imports
from ipt.db.images import Image
from ipt.db.base import session

def add_image(url):
    '''
        Adds the url to the database using the ORM and session object
        Parameter: url -> a url link sent from the user
        Returns: if there is no url a dict is returned -> statusCode: 400 error
                                                          body: {message: No URL was given}
                 else a dict is returned -> statusCode: 200 ok
                                            body: {message: image has been added to database}
    '''
    if url is None:
        return {
            'statusCode':400,
            'body':{
                'message':'No URL was given'
            }
        }
    image = Image(url=url,num_of_matches=0)
    session.add(image)
    session.commit()
    return {
        'statusCode':200,
        'body':{
            'message':'Image url has been added to Database'
        }
    }

def lambda_handler(event,context):
    '''
        Parameters: event -> the event that is sent to the endpoint
                context -> used for aws to specify lambda configuration in code
        Return: results found in the compare method which is a dictionary
    '''
    url = event.get('url',None)
    add_image_result = add_image(url)
    return add_image_result

