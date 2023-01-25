FROM python:3.11.1-slim-bullseye

ENV TARGET_HOST=
ENV TARGET_PATH=/oai/request/
ENV DB_HOST=
ENV DB_PATH=/graphql

# check every 1 day
ENV PUBDB_UPDATE_INTERVALVAL=86400
ENV OAI_REQUEST_INTERVAL=30
ENV LOG_LEVEL=DEBUG
ENV LIMIT_BATCH=-1
    
COPY requirements.txt /requirements.txt
COPY src/ /app/

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
      gcc \
      libxml2 \
      libxml2-dev \
      libxslt1.1 \
      libxslt1-dev \
    && \
    pip install -r requirements.txt && \
    DEBIAN_FRONTEND=noninteractive apt-get remove \
      -yq \
      --allow-downgrades \
      --allow-remove-essential \
      --allow-change-held-packages \
      gcc \
      libxml2-dev \
      libxslt1-dev \
    && \
    apt-get autoremove \
      -yq \
      --allow-downgrades \
      --allow-remove-essential \
      --allow-change-held-packages \
    && \
    apt-get clean && \ 
    rm requirements.txt && \
    groupadd -r app && \
    useradd --no-log-init -r -g app app && \
    chmod -R 775 /app

WORKDIR /app

USER app

CMD [ "python", "main.py" ]
