ARG BASE
FROM {BASE}

ARG DOMAIN
ARG CERT_NAME

ENV DOMAIN={DOMAIN}

RUN envsubst '${DOMAIN}' < nginx.conf > /etc/nginx/sites-available/redisfi.conf

WORKDIR /etc/nginx/sites-enabled
RUN ln -s ../sites-available/redisfi.conf .
RUN rm default

RUN certbot install --nginx -d ${DOMAIN} --cert-name={CERT_NAME} --redirect
