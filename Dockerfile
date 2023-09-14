FROM python:3.11.5-slim-bullseye
RUN apt-get update
RUN apt-get install -y wget curl git

ARG GITHUB_USERNAME
ARG GITHUB_ACCESS_TOKEN
ENV GITHUB_USERNAME=$GITHUB_USERNAME
ENV GITHUB_ACCESS_TOKEN=$GITHUB_ACCESS_TOKEN
RUN echo "machine github.com login $GITHUB_USERNAME password $GITHUB_ACCESS_TOKEN" > ~/.netrc

RUN git clone --no-checkout https://github.com/Botyto/BCloud.git /app
WORKDIR /app
RUN git sparse-checkout init
RUN git sparse-checkout set backend frontend docker
RUN git checkout HEAD

RUN apt-get install -y nodejs npm
WORKDIR /app/frontend
RUN npm install

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

CMD []
USER root
ENTRYPOINT ["python3", "/app/docker/entrypoint.py"]
