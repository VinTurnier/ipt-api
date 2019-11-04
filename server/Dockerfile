FROM python:3.5 as intermediate

WORKDIR /app 

ARG SSH_PRIVATE_KEY

RUN mkdir /root/.ssh/

RUN echo "${SSH_PRIVATE_KEY}" >> /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa

RUN touch /root/.ssh/known_hosts

RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

COPY ./private_repo_requirements.txt /app/private_repo_requirements.txt

RUN pip install -r private_repo_requirements.txt

FROM python:3.5

ARG Twilio_Account_SID

ARG Twilio_Auth_Token

COPY --from=intermediate /usr/local/lib/python3.5/site-packages/ /usr/local/lib/python3.5/site-packages/

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


