# pull python image
FROM python:slim

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN apt update && apt upgrade && pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# copy all local content to the image
COPY . /app

# let container listen at port 5000
EXPOSE 5000

# start the FLASK app
ADD start.sh /
RUN chmod +x /start.sh
CMD ["/start.sh"]