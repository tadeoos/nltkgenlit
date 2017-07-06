FROM python:3.5-slim
MAINTAINER Tadek Teleżyński "tadekte@gmail.com"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python -c "import nltk; nltk.download('punkt')"
CMD python server.py