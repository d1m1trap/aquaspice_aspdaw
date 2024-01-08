FROM python:3.8.2-slim-buster

WORKDIR /app
ADD . /app


RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

COPY requirements.txt /

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]