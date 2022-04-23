# Pull python image
FROM python:slim

# Create a volume
VOLUME /app

# Switch working directory
WORKDIR /app

# Let container listen at port 5006
EXPOSE 5006

# Install the dependencies and packages in the requirements file
RUN apt update -y && apt upgrade -y
COPY webapp/bokeh/requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Start the FLASK app
ENTRYPOINT ["bokeh", "serve", "/app/app.py", "--allow-websocket-origin=*"]