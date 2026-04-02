FROM node:18 AS frontend-builder
WORKDIR /app/frontend
COPY chat/frontend/package*.json ./
RUN npm install
COPY chat/frontend/ .
RUN npm run build

FROM python:3.12-slim
WORKDIR /app/backend
COPY chat/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY chat/ .
COPY db /app/db
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
