# FROM --platform=linux/x86_64 python:3.6-buster
# FROM --platform=linux/x86_64 python:3.9-slim-bullseye
FROM --platform=linux/x86_64 python:3.9-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client nano net-tools iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN ssh-keygen -q -t rsa -N '' -f /root/.ssh/id_rsa

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

VOLUME ['/app']

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]