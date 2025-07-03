#!/bin/bash
set -e

echo "Stopping all containers..."
docker-compose -f docker-compose.dev.yml down -v

echo "Cleaning up volumes..."
rm -rf ./volumes/*
mkdir -p ./volumes/{etcd,minio,milvus}

echo "Building and starting services..."
docker-compose -f docker-compose.dev.yml pull etcd minio standalone
docker-compose -f docker-compose.dev.yml build api

echo "Starting etcd..."
docker-compose -f docker-compose.dev.yml up -d etcd
sleep 10

echo "Starting minio..."
docker-compose -f docker-compose.dev.yml up -d minio
sleep 10

echo "Starting Milvus standalone..."
docker-compose -f docker-compose.dev.yml up -d standalone
sleep 20

echo "Checking Milvus health..."
max_retries=5
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    if curl -sf http://localhost:9091/healthz; then
        echo "Milvus is healthy"
        break
    fi
    echo "Waiting for Milvus to be healthy... (attempt $((retry_count + 1))/$max_retries)"
    sleep 10
    retry_count=$((retry_count + 1))
done

if [ $retry_count -eq $max_retries ]; then
    echo "Milvus failed to become healthy"
    docker-compose -f docker-compose.dev.yml logs standalone
    exit 1
fi

echo "Starting API..."
docker-compose -f docker-compose.dev.yml up -d api

echo "All services started. Checking logs..."
docker-compose -f docker-compose.dev.yml logs -f 