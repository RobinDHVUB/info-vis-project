# Pull python image
FROM python:slim

# Switch working directory
WORKDIR /app

# Let container listen at port 5006
EXPOSE 5006

# Install the dependencies and packages in the requirements file
RUN apt update -y && apt upgrade -y
COPY bokeh/requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Start the bokeh app
ENTRYPOINT ["panel", "serve", "panel.py", "--show", "--autoreload"]