FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY entry_api_server.py .
COPY ../entry-embedding/entry_python_rag_docs.json ./entry_python_rag_docs.json

EXPOSE 8000

CMD ["python", "entry_api_server.py"]
