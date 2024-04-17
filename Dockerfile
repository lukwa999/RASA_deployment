FROM python:3.9.13 AS BASE

RUN apt-get update \
    && apt-get --assume-yes --no-install-recommends install \
    build-essential \
    curl \
    git \
    jq \
    libgomp1 \
    vim

USER root

# Install pythainlp and spacy_pythainlp
RUN pip install rasa[full]==3.6.19
RUN pip install spacy==3.7.4
RUN pip install pythainlp==5.0.2
RUN pip install spacy-pythainlp==0.1
RUN pip install spacy-thai==0.7.3
RUN pip install tzdata
RUN python -m spacy download xx_sent_ud_sm
RUN pip install --no-cache-dir --upgrade pip
RUN pip install scipy==1.12.0
RUN pip install epitran
RUN pip install attacut
RUN pip install thai-nner

# Set working directory
WORKDIR /app

COPY . /app
COPY custom.py /app