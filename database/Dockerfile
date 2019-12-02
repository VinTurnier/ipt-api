From mysql:5.7

ENV MYSQL_ROOT_PASSWORD=password

ENV MYSQL_DATABASE=iptLocal

RUN apt-get update && apt-get install pv

WORKDIR /database/

RUN mkdir mysql-scripts

COPY ./get-production-db.sh /database/get-production-db.sh

COPY ./update-db.sh /database/update-db.sh

COPY ./.my.cnf /root/.my.cnf 

COPY ./mysql-scripts/ /docker-entrypoint-initdb.d/