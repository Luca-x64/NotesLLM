FROM python:3.14-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --root-user-action=ignore --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000


CMD ["fastapi", "run", "main.py", "--port", "8000"]
#CMD ["python", "connection.py"] # testing only