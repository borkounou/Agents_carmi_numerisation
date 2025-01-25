FROM python:3.10.12

RUN apt-get update && apt-get upgrade -qqy

RUN pip3 install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]