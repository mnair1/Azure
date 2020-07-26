FROM python:3.6-alpine

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY mongo.py .

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "mongo.py"]