FROM python:3-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
      pip install -r requirements.txt

COPY . .

RUN ls -la

CMD pytest ./tests  --capture=no
