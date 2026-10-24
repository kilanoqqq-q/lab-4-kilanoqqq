FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask pyftpdlib

EXPOSE 5000 8081 30000-30010

CMD ["python", "app.py"]
