FROM python:3.12.5-slim-bookworm

WORKDIR /app

# Environment
RUN apt-get update
RUN apt-get install -y bash nano postgresql-client build-essential
RUN pip install --upgrade pip

# Major pinned python dependencies
RUN pip install --no-cache-dir flake8==7.1.1 uWSGI==2.0.26 watchdog==5.0.1

# Regular Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt


# Copy our codebase into the container
COPY . .

ARG SECRET_KEY=
ARG DB_HOST=
ARG DB_NAME=
ARG DB_USER=
ARG DB_PASSWORD=
ARG REDIS_URL=

# Ops Parameters
ENV WORKERS=2
ENV PORT=80
ENV PYTHONUNBUFFERED=1

# chmod entrypoint
RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/entrypoint-celery.sh