from flask import Flask, request
from flask_cors import CORS

from ipt_api.compareImages import lambda_handler as compareImages
from ipt_api.addImageUrl import lambda_handler as addImageUrl
from ipt_api.sendMessage import lambda_handler as sendMessage


app = Flask(__name__)
CORS(app)

@app.route('/whatsapp',methods=['POST'])
def whatsapp():
    ''' 
        Post messages recieved from the link and sends back
        the message
    '''
    event = {
        "to": request.form.get('From'),
        "url": request.form.get('MediaUrl0'),
        "threshold":0.75
    }
    print(request.form)
    
    compare_status = compareImages.lambda_handler(event,{})
    if compare_status['image_in_db'] == 0:
        addImageUrl.lambda_handler(event,{})
        event['body'] = 'added new image to database'
        sendMessage.lambda_handler(event,{})
    else:
        event['body'] = compare_status.get('body','Pa gen Reponse')
        sendMessage.lambda_handler(event,{})
    
    return 'Nothing'



if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=6000)