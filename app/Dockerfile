FROM python:3.6.15-slim-buster
RUN pip3 install flask requests
RUN pip3 install flask_pymongo requests
RUN useradd pythonuser -ms /bin/bash
USER pythonuser
WORKDIR /app
COPY templates /app/
COPY app.py /app
CMD python -u app.py
