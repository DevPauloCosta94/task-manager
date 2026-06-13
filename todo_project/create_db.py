#!/usr/bin/env python
"""
Script para inicializar o banco de dados SQLite.
Cria as tabelas se não existirem.
"""
from todo_project import app, db

if __name__ == '__main__':
    with app.app_context():
        print("Criando tabelas do banco de dados...")
        db.create_all()
        print("Banco de dados inicializado com sucesso!")
