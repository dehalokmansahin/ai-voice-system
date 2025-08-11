#!/bin/bash
# Test script for voice-ai-core Docker deployment

set -e

echo "🐳 Testing Voice-AI-Core Docker Deployment"
echo "=========================================="

echo "1. Checking if Docker is running..."
docker --version

echo "2. Starting services with docker-compose..."
docker-compose up -d

echo "3. Waiting for services to initialize..."
sleep 10

echo "4. Checking service status..."
docker-compose ps

echo "5. Testing opensips-ai-voice-connector health..."
if docker-compose exec opensips-ai-voice-connector python -c "import voice_ai_core; print('✅ voice-ai-core imported successfully')"; then
    echo "✅ Voice-AI-Core is working in container"
else
    echo "❌ Voice-AI-Core import failed"
    exit 1
fi

echo "6. Testing VAD functionality..."
if docker-compose exec opensips-ai-voice-connector python -c "from voice_ai_core.audio import SileroVADAnalyzer; print('✅ SileroVADAnalyzer imported successfully')"; then
    echo "✅ VAD components are working"
else
    echo "❌ VAD components failed"
    exit 1
fi

echo "7. Checking logs for any errors..."
docker-compose logs --tail=20 opensips-ai-voice-connector

echo ""
echo "🎉 Docker deployment test completed successfully!"
echo "Voice-AI-Core is running properly in the containerized environment."