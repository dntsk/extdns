FROM python:3.9

WORKDIR /opt

COPY requirements.txt ./
RUN pip install --no-cache -r requirements.txt
COPY . ./

CMD ["python", "./server.py"]
