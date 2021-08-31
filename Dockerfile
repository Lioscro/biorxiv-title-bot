FROM python:3.8-bullseye

WORKDIR /home/root
COPY requirements.txt .
RUN pip install -r requirements.txt
