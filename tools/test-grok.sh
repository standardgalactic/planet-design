#!/usr/bin/bash

curl https://api.x.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <api-key>" \
  -d '{
    "messages": [
      { "role": "system", "content": "You are a test assistant." },
      { "role": "user", "content": "What is the purpose of a null-wavefront in Null Convention Logic?" }
    ],
    "model": "grok-3-latest",
    "stream": false,
    "temperature": 0
  }'

