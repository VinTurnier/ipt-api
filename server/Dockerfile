FROM python:3.5

ARG Twilio_Account_SID

ARG Twilio_Auth_Token

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /app/requirements.txt 

WORKDIR /app

RUN pip3 install -r requirements.txt 

COPY ./ /app

ENV IPT_CONNECTION_STRING='mysql+pymysql://root:password@ipt_local_db/ipt_local'

ENV Twilio_Account_SID='${Twilio_Account_SID}'

ENV Twilio_Auth_Token='${Twilio_Auth_Token}'

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]


