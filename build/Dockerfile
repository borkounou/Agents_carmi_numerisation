FROM python:3.10.12

RUN apt-get update && apt-get upgrade -qqy

COPY build/requirements.txt /archicarmi-app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]