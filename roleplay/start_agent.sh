#!/bin/bash

# Roleplay Agent 起動スクリプト

set -e

echo "============================================"
echo "  Roleplay Agent - Build & Start"
echo "============================================"
echo ""

# 現在のディレクトリを確認
if [ ! -f "agent_worker.py" ]; then
    echo "❌ agent_worker.py not found!"
    echo "Please run this script from agents/roleplay directory"
    exit 1
fi

# .envファイルの確認
if [ ! -f "../../.env" ]; then
    echo "❌ .env file not found at project root!"
    exit 1
fi

echo "🔨 Building Docker image..."
docker build -t roleplay-agent .

echo ""
echo "🚀 Starting agent..."
echo ""

# Docker networkが存在するか確認
if ! docker network ls | grep -q "ai-roleplay-exp_default"; then
    echo "⚠️  Docker network 'ai-roleplay-exp_default' not found"
    echo "Please start backend services first:"
    echo "  cd /home/ubuntu/ai-roleplay-exp"
    echo "  ./start_all.sh"
    exit 1
fi

# Agentを起動
docker run --rm \
  --name roleplay-agent \
  --network ai-roleplay-exp_default \
  --env-file ../../.env \
  roleplay-agent dev

echo ""
echo "✅ Agent started successfully"
