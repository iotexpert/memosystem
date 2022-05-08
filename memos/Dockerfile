# Use the Python3.8.3 image
FROM python:3.8-bullseye
ENV APP=/app

RUN apt-get update && apt-get install -y python3-dev gcc  libc-dev libsasl2-dev python-dev libldap2-dev libssl-dev

# Set the working directory to /app
WORKDIR $APP

# Copy the current directory contents into the container at /app 
ADD . $APP



RUN python3 -m venv env
ENV PATH="$APP/env/bin:$PATH"


# Install the dependencies
RUN pip install -r requirements.txt

# run the command to start uWSGI
#CMD ["uwsgi", "app.ini"]




# Install dependencies:
#COPY requirements.txt .
#RUN pip install -r requirements.txt

# Run the application:
#COPY myapp.py .

#RUN python3 create_db.py

CMD ["flask", "run","--host=0.0.0.0"]