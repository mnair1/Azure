FROM python:3.6-alpine

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY mongo.py .

COPY requirements.txt .

# RUN apk add --no-cache git gcc python3-dev gpgme-dev libc-dev

RUN pip install -r requirements.txt

EXPOSE 5000

# CMD ["python", "mongo.py", "runserver", "--host", "0.0.0.0"]
CMD ["python", "mongo.py"]
