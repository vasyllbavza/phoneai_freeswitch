
docker build -t phoneai .

docker run -it -d  -p 8000:8000 --name phoneai -v ./:/app  phoneai

docker exec -it phoneai  bash