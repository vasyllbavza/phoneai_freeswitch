
docker build -t phoneai .

docker run -itd -p 8000:8000 --name phoneai -v /Users/mohammadkamruzzaman/mywork1/phoneAI/code/phoneai_freeswitch/api_code:/app --platform=linux/x86_64  phoneai

docker exec -it phoneai  bash