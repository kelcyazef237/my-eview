FROM python:3.12-slim

WORKDIR /app

# System deps for WeasyPrint (libpango, libcairo), psycopg2 (libpq), nmap
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf2.0-0 \
    libpq5 gcc libpq-dev \
    nmap \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]