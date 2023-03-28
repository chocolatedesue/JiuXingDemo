FROM python:3.11.2-slim-bullseye

# ENV 
EXPOSE 8000
WORKDIR /root/app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY app.py crud.py models.py database.py logs.ini schemas.py  ./
COPY scripts scripts
COPY util util
COPY restModel restModel

ENTRYPOINT [ "/root/app/scripts/run.sh" ]