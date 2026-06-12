FROM python:3.12-slim
WORKDIR /app
COPY microservices/services/certificate-service/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY microservices/services/certificate-service/app ./app
COPY shared ./shared
COPY microservices/services/certificate-service/alembic ./alembic
COPY microservices/services/certificate-service/alembic.ini ./
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
