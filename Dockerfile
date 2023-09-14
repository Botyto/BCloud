FROM python:3.12-rc-alpine

COPY . /app

WORKDIR /app/backend
RUN pip install -r requirements.txt

RUN apk add --no-cache nodejs npm
WORKDIR /app/frontend
RUN npm install

RUN apt-get install -y nginx
RUN mkdir -p /var/lib/nginx
RUN chmod -R 777 /var/lib/nginx
RUN mkdir -p /var/log/nginx
RUN chmod -R 777 /var/log/nginx

