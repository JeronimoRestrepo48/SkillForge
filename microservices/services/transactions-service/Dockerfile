FROM python:3.12-slim
WORKDIR /app
COPY microservices/services/transactions-service/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY microservices/services/transactions-service/app ./app
COPY shared ./shared
COPY microservices/services/transactions-service/alembic ./alembic
COPY microservices/services/transactions-service/alembic.ini ./
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
