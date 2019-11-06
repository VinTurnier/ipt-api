import os
from twilio.rest import Client


account_sid = os.environ.get('Twilio_Account_SID')
auth_token = os.environ.get('Twilio_Auth_Token')

client = Client(account_sid,auth_token)


def create_message(to,body):
    print('sending message...')
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=body,
        to=to,
    )
    return message

def lambda_handler(event,context):
    body = event.get('body',None)
    to = event.get('to',None)
    message = create_message(to,body)
    return message