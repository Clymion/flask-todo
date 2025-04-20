#!/bin/bash
set -e

# GCloudプロジェクト設定
PROJECT_ID="valiant-circuit-432308-v5"
REGION="asia-northeast1"

gcloud config set project ${PROJECT_ID}

# Cloud BuildにDockerイメージをビルドして、GCRにプッシュ
REPOSITORY_NAME="flask-todo-api"
SERVICE_NAME="flask-api-image"
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}/${SERVICE_NAME}"
IMAGE_TAG="latest"
echo "Building Docker image..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
docker push ${IMAGE_NAME}:${IMAGE_TAG}

# Cloud Runにデプロイ
echo "Deploying to Cloud Run..."
gcloud run deploy ${REPOSITORY_NAME} \
  --image ${IMAGE_NAME}:${IMAGE_TAG} \
  --platform managed \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --allow-unauthenticated
