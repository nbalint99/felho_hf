FROM python:3.6.15-slim-buster
RUN pip3 install flask requests
RUN useradd pythonuser -ms /bin/bash
WORKDIR /home/pythonuser/app
USER pythonuser
COPY app.py app.py
CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
CMD python -u app.py
