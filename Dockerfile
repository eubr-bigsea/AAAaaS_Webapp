# Base image
FROM alpine:3.4


COPY ./ /usr/src/app

WORKDIR /usr/src/app

# Installing needed packages
RUN apk add --update --no-cache python3 \
 && apk add --update --no-cache --virtual .build-deps gcc libc-dev python3 python3-dev

RUN apk update && apk add build-base libffi-dev

EXPOSE 9000

# Install requirements
ADD aaa_manager/requirements.txt /usr/src/app/aaa_manager/
RUN pip3 install --no-cache-dir -q --upgrade pip \
 && pip3 install --no-cache-dir -r aaa_manager/requirements.txt \
 && rm -rf ~/.cache/pip/*
 
#RUN python3 db_scripts/create_mongo_user.py

ENV AUTH_DB_PORT 5432
ENV AUTH_DB_HOST localhost
ENV MESOS_DNS_IP_PORT http://158.42.105.24:8123
ENV MESOS_DNS_AUTH_DB_ID _auth-db-auth._tcp.marathon.mesos

# Run server. gunicorn -u is need for docker-compose (needs unbuffered output)
CMD python3 setup.py develop && gunicorn --reload --log-level DEBUG --paste development.ini \
&& python3 db_scripts/create_mongo_user.py --mesosdns "${MESOS_DNS_IP_PORT}" \
    --mesosdns_db "${MESOS_DNS_AUTH_DB_ID}" \
    --vars db_scripts/vars.rc

