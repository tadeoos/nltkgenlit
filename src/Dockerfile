FROM python:3
MAINTAINER Tadek Teleżyński "tadekte@gmail.com"
RUN apt-get update -y
RUN apt-get install -y aha tree
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python -c "import nltk; nltk.download('punkt')"
CMD python server.py