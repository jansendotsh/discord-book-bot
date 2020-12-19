FROM python:3.8.6
WORKDIR /usr/src/app
COPY requirements.txt ./
COPY main.py ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p db/
CMD [ "python", "./main.py" ]