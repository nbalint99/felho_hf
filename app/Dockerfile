FROM python:3.6.15-slim-buster
RUN pip3 install flask requests
RUN pip3 install flask_pymongo requests
RUN useradd pythonuser -ms /bin/bash
WORKDIR /app
USER pythonuser
COPY app.py app.py
CMD python -u app.py
