FROM python:3.8-slim
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libgtk2.0-dev \
    build-essential \
    cmake \
    wget \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip
RUN pip3 install flask requests
RUN pip3 install flask_pymongo requests
RUN pip install --upgrade pip setuptools wheel
RUN pip install opencv-python-headless
RUN pip install darknet
RUN pip install Flask-Mail
RUN pip install sendgrid
RUN mkdir -p /app/other_config
RUN mkdir -p /app/uploads && chmod 777 /app/uploads
RUN wget -O /app/other_config/yolov3.weights "https://pjreddie.com/media/files/yolov3.weights"
RUN useradd pythonuser -ms /bin/bash
USER pythonuser
WORKDIR /app
COPY templates /app/templates
COPY app.py /app
COPY config /app/config
ENV SENDGRID_API_KEY=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
CMD python -u app.py
