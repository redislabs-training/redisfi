FROM python:3.9-alpine
RUN apk update
RUN apk add g++ gcc libxslt-dev libffi-dev python3-dev musl-dev make
RUN pip3 install --upgrade pip
RUN pip3 install poetry


ENV INSTALL_DIR=/opt/redisfi
WORKDIR ${INSTALL_DIR}
COPY pyproject.toml .

# this takes a LONG time to do. This should cache so we only have to install with changes to pyproject.toml
RUN poetry install 

# Development workaround - make sure we don't override poetry.lock inside the container with one we're copying from local
RUN mv poetry.lock poetry.lock.bak
COPY . .
RUN mv poetry.lock.bak poetry.lock


