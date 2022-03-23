docker stop iv-container
docker rm iv-container

cd ..

cd webapp
docker build -t infoviz:latest .
docker run --name iv-container -d -p 5000:5000 infoviz:latest