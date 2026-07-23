#!/usr/bin/env bash

# Intercepta Ctrl+C (SIGINT) e SIGTERM para encerrar os dois processos filhos
cleanup() {
    echo ""
    echo "========================================="
    echo " Encerrando Backend e Frontend..."
    echo "========================================="
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup INT TERM EXIT

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export NODE_OPTIONS="--localstorage-file=/tmp/node_storage"

echo "========================================="
echo " Iniciando Servidores do Projeto ELiS OCR"
echo "========================================="

# 1. Iniciar Backend (Flask) via uv
echo "[Backend] Subindo servidor Flask na porta 5000..."
(cd "$ROOT_DIR" && uv run python backend/app.py) &

# 2. Iniciar Frontend (Vue.js) via npm
echo "[Frontend] Subindo servidor de desenvolvimento Vue..."
(cd "$ROOT_DIR/frontend" && npm run serve) &

# Aguarda a execução dos processos
wait
