FROM python:3.9-slim

RUN apt-get update

WORKDIR /app
COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN mkdir -p /app/logs
COPY .config/earthengine/credentials /root/.config/earthengine/credentials

CMD ["sh", "-c", "python3 /app/src/main.py"]


