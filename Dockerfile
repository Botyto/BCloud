FROM python:3.11.5-slim-bullseye
RUN apt-get update
RUN apt-get install -y wget curl

COPY frontend /app/frontend
COPY docker/frontend.nginx.conf /frontend.nginx.conf
RUN apt-get install -y nodejs npm
WORKDIR /app/frontend
RUN npm install

COPY backend /app/backend
COPY docker/backend.nginx.conf /backend.nginx.conf
WORKDIR /app/backend
RUN apt-get install -y libmariadb-dev libmariadb3
RUN pip install -r requirements.txt

RUN apt-get install -y nginx
RUN mkdir -p /var/lib/nginx
RUN chmod -R 777 /var/lib/nginx
RUN mkdir -p /var/log/nginx
RUN chmod -R 777 /var/log/nginx
RUN rm /etc/nginx/nginx.conf
COPY docker/nginx.conf /etc/nginx/nginx.conf

COPY docker/entrypoint.py /entrypoint.py
CMD []
USER root
ENTRYPOINT ["python3", "/entrypoint.py"]
