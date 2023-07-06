FROM python:3

ADD . /app

WORKDIR /app

# This is to run our scripts headlessly (without a display)
RUN apt-get update && apt-get install -y xvfb xorg

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py /app/app.py

# Set the entry point to run the app.py script
ENTRYPOINT [ "python", "/app/app.py" ]