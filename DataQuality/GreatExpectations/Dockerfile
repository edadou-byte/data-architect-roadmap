FROM python:3.11-slim

RUN apt-get update && apt-get install -y openjdk-17-jre-headless && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME_OVERRIDE=/usr/lib/jvm/java-17-openjdk-amd64

WORKDIR /app
COPY . /app/
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "main.py"]