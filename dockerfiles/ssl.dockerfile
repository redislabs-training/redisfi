FROM python:3.9

RUN apt update
RUN apt install -y nginx gcc musl-dev libffi-dev curl git rustc openssl gettext-base
RUN pip3 install --upgrade pip
RUN pip3 install poetry certbot-nginx certbot-dns-google

ARG GCP_AUTH
ARG NOTIFICATION_EMAIL
ARG DOMAIN
ARG STAGING=--test-cert

WORKDIR /tmp
RUN echo ${GCP_AUTH} > /tmp/auth.json && chmod 600 /tmp/auth.json && certbot certonly ${STAGING} --dns-google -d ${DOMAIN} -m ${NOTIFICATION_EMAIL} --agree-tos --dns-google-credentials=/tmp/auth.json && rm /tmp/auth.json