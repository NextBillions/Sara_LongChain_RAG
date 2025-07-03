#!/bin/bash

# 停止并删除所有相关容器和卷
docker-compose down -v

# 清理旧的数据目录
rm -rf ./volumes/*

# 创建必要的目录
mkdir -p ./volumes/{etcd,minio,milvus,neo4j/{data,logs}}

# 拉取最新镜像
docker-compose pull

# 按顺序启动服务
echo "Starting etcd..."
docker-compose up -d etcd
sleep 5

echo "Starting minio..."
docker-compose up -d minio
sleep 5

echo "Starting Milvus standalone..."
docker-compose up -d standalone
sleep 10

echo "Starting API..."
docker-compose up -d api
sleep 5

echo "Starting Neo4j..."
docker-compose up -d graph

# 检查服务状态
echo "Checking service status..."
docker-compose ps

# 检查日志
echo "Checking logs..."
docker-compose logs 