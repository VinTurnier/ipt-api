IPT Project
===

IPT (Information Pou Tout) is a project that is to help identify if pictures where already posted, and when they were posted. Users send pictures to a phone number, then that same number responds with a text message. There are two possible text messages. The first one is to let the user know that the image has been added to the database because it was not found in it. The second one is to let the user know that the image was found. When an image is found the message gives the percentage that the image compared to the one in the database, then it also lets you know the date that the images was first added to the database. 

# Python App Setup
To setup your environment to run this application, you must first start a virtual environment in python. You can do this by simply running the [virtualenv command](https://virtualenv.pypa.io/en/latest/installation/):
```s
virtualenv -p python3 venv
```
Then start the virtualenv file that you just created:
```s
source venv/bin/activate
```
You should see now that your terminal is in a virtual environment. Once in the environment there are a couple packages to install to run `app.py`. All of the necessary packages are in the `requirements.txt` file. Run pip install on the file to install the necessary packages.
```s
pip install -r requirements.txt
```
Once that is completed, you should be able to run the `app.py` file and lauch your flask server.
```s
python app.py
```

# Twilio Setup
After setting up python you want to setup twilio to test locally. I normally use [ngrok](https://dashboard.ngrok.com/get-started) and run the command locally to expose my [local host to the interweb](https://vmokshagroup.com/blog/expose-your-localhost-to-web-in-50-seconds-using-ngrok/). I normally move the executable `ngrok` file to my `/usr/local/bin` directory, so that i can execute from anywhere on my computer. Once you have `ngrok` installed, run the following command to connect it to your localhost:
```s
ngrok http 6000
```
Now that your localhost is exposed to the outside world, you can add it to twilio whatsapp portal. To reach the portal, go on [twilio](https://www.twilio.com/login), login to your account, go to programable sms, which is located on the left with a chat icon, click whatsapp, lastly go into the sandox. Where it says "when a message comes in", add your ngrok forwarding link like this:
```s
http://d71ece38.ngrok.io/whatsapp
```
The `/whatsapp` is the route to the flask server `whatsapp` method.

Once that is setup, the last thing you will need to do is to identify the phone number that you will whatsapp. This can be found in the Whatsapp page on the twilio website by clicking on `Learn`. There you will see the phone number to whatsapp to just play arround with the api. Make sure to change the number in the `sendMessage/lambda_handler.py` to the number that is on the website.

# MySQL Database Setup


# Using App
Now that you have everything setup and running, you can now send picture to that number on whatsapp, and it will return you the status of the picture.

Contribution
===


-e git+ssh://git@github.com/vinturnier/ipt-models.git@cf87525746f400e52fd12f47262186746f5eef57#egg=ipt