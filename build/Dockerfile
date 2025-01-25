FROM python:3.10.12

RUN apt-get update && apt-get upgrade -qqy

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]