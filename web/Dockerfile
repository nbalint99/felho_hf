FROM python:3.6.15-slim-buster
RUN pip3 install flask requests
RUN useradd pythonuser -ms /bin/bash
WORKDIR /home/pythonuser/web
USER pythonuser
COPY web.py web.py
CMD python -u web.py
