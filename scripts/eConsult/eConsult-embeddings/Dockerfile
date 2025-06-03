FROM python:3.11-slim
LABEL authors="nodiryuldashev"

WORKDIR /usr/src/app

# install requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

# run
#RUN apt-get install ca-certificates
#RUN update-ca-certificates
ENV PORT=8000
#ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
#ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
SHELL ["/bin/bash", "-c"]
CMD python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT}
