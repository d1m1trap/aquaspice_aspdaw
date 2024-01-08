# app/Dockerfile

FROM python:3.8.2-slim-buster

WORKDIR /app
ADD . /app

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

COPY requirements.txt /

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "descriptive.py", "--server.port=8501", "--server.address=0.0.0.0"]