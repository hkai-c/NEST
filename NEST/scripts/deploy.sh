#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 打印带颜色的信息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

# 检查必要的命令
print_info "Checking required commands..."
check_command docker
check_command kubectl
check_command nvidia-smi

# 检查NVIDIA驱动
print_info "Checking NVIDIA driver..."
if ! nvidia-smi &> /dev/null; then
    print_error "NVIDIA driver is not properly installed"
    exit 1
fi

# 创建必要的目录
print_info "Creating necessary directories..."
mkdir -p data/postgres
mkdir -p data/mongodb
mkdir -p data/rabbitmq

# 构建Docker镜像
print_info "Building Docker images..."
cd backend
docker build -t nest-backend:latest . || { print_error "Failed to build backend image"; exit 1; }
cd ../frontend
docker build -t nest-frontend:latest . || { print_error "Failed to build frontend image"; exit 1; }
cd ..

# 创建Kubernetes命名空间
print_info "Creating Kubernetes namespace..."
kubectl create namespace nest --dry-run=client -o yaml | kubectl apply -f -

# 部署基础设施
print_info "Deploying infrastructure components..."
kubectl apply -f infrastructure/k8s/pvc.yaml
kubectl apply -f infrastructure/k8s/secrets.yaml
kubectl apply -f infrastructure/k8s/database-deployment.yaml
kubectl apply -f infrastructure/k8s/rabbitmq-deployment.yaml

# 等待数据库就绪
print_info "Waiting for databases to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n nest --timeout=300s
kubectl wait --for=condition=ready pod -l app=mongodb -n nest --timeout=300s

# 部署后端服务
print_info "Deploying backend services..."
kubectl apply -f infrastructure/k8s/backend-deployment.yaml

# 等待所有pod就绪
print_info "Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n nest --timeout=300s

# 检查部署状态
print_info "Checking deployment status..."
kubectl get pods -n nest
kubectl get services -n nest

print_info "Deployment completed! You can check the status of your deployment using:"
echo "kubectl get pods -n nest"
echo "kubectl get services -n nest"
echo "kubectl logs -f <pod-name> -n nest" 