FROM python:3.6.15-slim-buster
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libgtk2.0-dev \
    build-essential \
    cmake \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip
RUN pip3 install flask requests
RUN pip3 install flask_pymongo requests
RUN pip install --upgrade pip setuptools wheel
RUN pip install opencv-python-headless
RUN useradd pythonuser -ms /bin/bash
USER pythonuser
WORKDIR /app
COPY templates /app/templates
COPY app.py /app
CMD python -u app.py
