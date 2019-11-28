# Standard Library Imports
import os

# Third Party Imports
from twilio.rest import Client


account_sid = os.environ.get('Twilio_Account_SID')
auth_token = os.environ.get('Twilio_Auth_Token')

client = Client(account_sid,auth_token)


def create_message(to,body):
    '''
        Creates the message that will be sent to the user from the whatsapp phone number
        Parameters: to -> the phone number of where the message is going to
                    body -> The message that is being sent
        Returns: message -> returns the message object that was created
    '''
    print('sending message...')
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=body,
        to=to,
    )
    return message

def lambda_handler(event,context):
    '''
        Parameters: event -> takes in a dictionary containing body and to as keys
                    context -> used for aws lambda to know where the lambda is being used from basically in what context
        Returns: message -> message that was created
    '''
    body = event.get('body',None)
    to = event.get('to',None)
    message = create_message(to,body)
    return message