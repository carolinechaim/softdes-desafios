FROM python:3.8

# set a directory for the app
WORKDIR /usr/src/app

# copy all the files to the container
COPY . .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# What port you will be working in
EXPOSE 5000

CMD ["python", "./softdes.py"]

