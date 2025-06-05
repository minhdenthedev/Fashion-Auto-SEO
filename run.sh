#!/bin/bash

sudo docker pull khanh50105010/nginx
sudo docker pull khanh50105010/mysql
sudo docker pull khanh50105010/minio
sudo docker pull khanh50105010/fashion-captioner-ai_advise
sudo docker pull khanh50105010/fashion-captioner-ai_caption
sudo docker pull khanh50105010/fashion-captioner-app

sudo docker stop mysql nginx minio ai-caption ai-advise app
sudo docker rm mysql nginx minio ai-caption ai-advise app
sudo docker run -d \
  -p 3307:3306 \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=1234 \
  khanh50105010/mysql:8

sudo docker run -d -p 80:80 --name nginx khanh50105010/nginx
 
sudo docker run -d \
  -p 9000:9000 \
  --name minio \
  -v /home/m1nhd3n/minio-data:/data \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  khanh50105010/minio server /data

sudo docker run -d -p 8000:8000 --name ai-caption khanh50105010/fashion-captioner-ai_caption

sudo docker run -d -p 5000:5000 --name ai-advise khanh50105010/fashion-captioner-ai_advise

sudo docker run -d -p 8081:8081 --name app khanh50105010/fashion-captioner-app
