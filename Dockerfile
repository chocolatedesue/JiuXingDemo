FROM python:3.10
EXPOSE 8000
WORKDIR /root/app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT [ "./scripts/run.sh" ]