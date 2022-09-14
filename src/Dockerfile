FROM python:3.9.3

# set a directory for the app
WORKDIR /usr/src/app

# copy all the files to the container
COPY adduser.py ./
COPY desafio.py ./
COPY quiz.db ./
COPY softdes.py ./
COPY users.csv ./

# install dependencies
RUN python -m pip install --upgrade pip
RUN pip install --upgrade --force-reinstall --no-cache-dir flask_httpauth 
RUN pip freeze > requirements.txt


RUN python adduser.py

# What port you will be working in
EXPOSE 8080

CMD ["python", "./softdes.py"]

