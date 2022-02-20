FROM python:3.9-alpine
RUN apk update
RUN apk add g++ gcc libxslt-dev libffi-dev python3-dev musl-dev make
RUN pip3 install --upgrade pip
RUN pip3 install poetry


ENV INSTALL_DIR=/opt/redisfi
WORKDIR ${INSTALL_DIR}
COPY . .

# we don't need to virtualize a virtualization
RUN poetry config virtualenvs.create false 
RUN poetry install 

