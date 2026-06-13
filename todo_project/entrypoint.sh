#!/bin/bash
set -e

echo "Inicializando banco de dados..."
python create_db.py

echo "Iniciando aplicação com gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 run:app
