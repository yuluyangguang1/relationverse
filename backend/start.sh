#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export LLM_API_KEY="sk-api-js8Sj8OpAcvJ6HxtS7ydfv08kU0c_uI5Y7jin-e1o82ZbZYi5F3mtg8AFmhP62Z0cUrVMa85uzbX9cIGxoB-oIiAzfkz8NRxSTXC2FIQpJb9LKDhJlekJQE"
export LLM_API_BASE="https://api.minimax.chat/v1"
export LLM_MODEL="MiniMax-Text-01"
exec uvicorn main:app --host 0.0.0.0 --port 8000
