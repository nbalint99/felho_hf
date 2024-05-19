FROM python:3.6.15-slim-buster
RUN pip3 install flask requests
RUN pip3 install flask_pymongo requests
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libgtk2.0-dev \
    && rm -rf /var/lib/apt/lists/*
RUN useradd pythonuser -ms /bin/bash
USER pythonuser
WORKDIR /app
COPY templates /app/templates
COPY app.py /app
CMD python -u app.py
