#!/bin/bash
# Health check script for Docker container

# Check if the application is responding
if curl -f -s --max-time 10 http://localhost:5000/health > /dev/null 2>&1; then
    echo "Health check passed"
    exit 0
else
    echo "Health check failed"
    exit 1
fi