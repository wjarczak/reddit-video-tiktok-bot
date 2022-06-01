FROM python:latest
LABEL Maintainer="wjarczak"
COPY . /opt/app
WORKDIR /opt/app
RUN pip install -r requirements.txt
RUN playwright install \
	playwright install-deps
CMD [ "python", "./main.py"]