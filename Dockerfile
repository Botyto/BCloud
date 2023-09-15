# Frontend build

FROM node:20-bullseye-slim AS frontend
RUN apt-get update
RUN apt-get install -y git

ARG GITHUB_ACCESS_TOKEN
RUN git clone --no-checkout https://$GITHUB_ACCESS_TOKEN@github.com/Botyto/BCloud.git /app
WORKDIR /app
RUN git sparse-checkout init
RUN git sparse-checkout set frontend
RUN git checkout HEAD

WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Runtime

FROM python:3.11.5-slim-bullseye
RUN apt-get update
RUN apt-get install -y wget curl git

RUN apt-get install -y nginx
RUN mkdir -p /var/lib/nginx && chmod -R 777 /var/lib/nginx
RUN mkdir -p /var/log/nginx && chmod -R 777 /var/log/nginx

RUN apt-get install -y libmariadb-dev libmariadb3

ARG GITHUB_ACCESS_TOKEN
RUN git clone --no-checkout https://$GITHUB_ACCESS_TOKEN@github.com/Botyto/BCloud.git /app
WORKDIR /app
RUN git sparse-checkout init
RUN git sparse-checkout set backend docker
RUN git checkout HEAD

WORKDIR /app/frontend
COPY --from=frontend /app/frontend/dist /app/frontend/dist

WORKDIR /app/backend
RUN pip install -r requirements.txt

RUN rm /etc/nginx/nginx.conf
RUN mv /app/docker/nginx.conf /etc/nginx/nginx.conf

RUN mkdir /data
WORKDIR /data
VOLUME /data
EXPOSE 80
USER root
ENTRYPOINT ["python3", "/app/docker/entrypoint.py"]
