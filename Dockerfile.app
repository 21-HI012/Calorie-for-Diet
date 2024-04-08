FROM python:3.10

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx libzbar0 && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir -r requirements.txt

ENV FLASK_APP=__init__.py

EXPOSE 5000

ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]
