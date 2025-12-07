#/backend/Dockerfile
FROM python:3.12-slim

# application 
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy python modules & scripts
COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
