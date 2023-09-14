FROM python:3.12-rc-alpine

COPY ../frontend /app/frontend
COPY backend.nginx.conf /backend.nginx.conf
RUN apk add --no-cache nodejs npm
WORKDIR /app/frontend
RUN npm install

COPY ../backend /app/backend
COPY frontend.nginx.conf /frontend.nginx.conf
WORKDIR /app/backend
RUN pip install -r requirements.txt

RUN apt-get install -y nginx
RUN mkdir -p /var/lib/nginx
RUN chmod -R 777 /var/lib/nginx
RUN mkdir -p /var/log/nginx
RUN chmod -R 777 /var/log/nginx
RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

COPY entrypoint.py /entrypoint.py
CMD []
USER root
ENTRYPOINT ["/venv/synapse/bin/python", "/entrypoint.py"]
