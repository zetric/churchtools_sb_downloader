FROM python:3.14.6-slim-trixie

WORKDIR /usr/source/app

COPY ./ ./

RUN apt update && apt upgrade -y
RUN pip install --no-cache-dir -r requirements.yaml

CMD [ "python", "./app.py" ]
    