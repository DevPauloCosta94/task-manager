#!/usr/bin/env python
"""
Script de varredura completa das tabelas do banco de dados SQLite.
Verifica sincronização entre modelos e tabelas, estrutura, e integridade.
"""
import sys
from pathlib import Path
from todo_project import app, db
from todo_project.models import User, Task

def print_header(title):
    """Imprime um cabeçalho formatado"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def check_database_status():
    """Verifica status geral do banco de dados"""
    print_header("1. STATUS DO BANCO DE DADOS")
    
    # Tentar descobrir o caminho do SQLite a partir do engine URL
    try:
        db_url = str(db.engine.url)
    except Exception:
        db_url = None

    db_path = None
    if db_url and db_url.startswith('sqlite'):
        # Extrair o caminho do arquivo a partir do URL (ex: sqlite:////app/instance/site.db)
        import re
        path_part = db_url.split(':', 1)[1]
        # Normalizar múltiplas barras iniciais para uma única barra (caminho absoluto)
        path = re.sub(r'^/+', '/', path_part)
        db_path = Path(path)

    if db_path and db_path.exists():
        print(f"✓ Banco de dados existe: {db_path}")
        print(f"  Tamanho: {db_path.stat().st_size} bytes")
        return True
    else:
        # Fallback: procurar por arquivos .db comuns em /app/instance ou /app
        candidates = [Path('/app/instance/site.db'), Path('/app/site.db'), Path('/site.db')]
        for c in candidates:
            if c.exists():
                print(f"✓ Banco de dados encontrado (fallback): {c}")
                return True
        print(f"✗ Banco de dados NÃO encontrado. Esperado em: {db_path or 'sqlite:///...'}")
        return False

def list_all_tables():
    """Lista todas as tabelas no banco de dados"""
    print_header("2. TABELAS NO BANCO DE DADOS")
    
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print("✗ Nenhuma tabela encontrada!")
        return []
    
    print(f"✓ Total de tabelas: {len(tables)}\n")
    for table in sorted(tables):
        print(f"  - {table}")
    
    return tables

def check_table_structure(table_name):
    """Verifica estrutura de uma tabela específica"""
    inspector = db.inspect(db.engine)
    columns = inspector.get_columns(table_name)
    pk = inspector.get_pk_constraint(table_name)
    fks = inspector.get_foreign_keys(table_name)
    
    print(f"\n  Tabela: {table_name}")
    print(f"  {'─' * 70}")
    
    # Colunas
    print(f"  Colunas ({len(columns)}):")
    for col in columns:
        nullable = "✓ NULL" if col['nullable'] else "✗ NOT NULL"
        print(f"    - {col['name']:20} {str(col['type']):15} {nullable}")
    
    # Chave primária
    if pk and pk.get('constrained_columns'):
        print(f"  Chave Primária: {', '.join(pk['constrained_columns'])}")
    
    # Chaves estrangeiras
    if fks:
        print(f"  Chaves Estrangeiras ({len(fks)}):")
        for fk in fks:
            print(f"    - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
    else:
        print(f"  Chaves Estrangeiras: Nenhuma")

def check_table_data(table_name):
    """Conta registros em uma tabela"""
    result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table_name}"))
    count = result.scalar()
    print(f"  Registros: {count}")

def validate_models_vs_tables(tables):
    """Valida se os modelos correspondem às tabelas"""
    print_header("3. VALIDAÇÃO: MODELOS vs TABELAS")
    
    expected_models = {
        'user': User,
        'task': Task
    }
    
    for model_table, model_class in expected_models.items():
        if model_table in tables:
            print(f"✓ {model_class.__name__:15} → Tabela '{model_table}' EXISTS")
        else:
            print(f"✗ {model_class.__name__:15} → Tabela '{model_table}' MISSING!")
    
    # Verificar tabelas extras
    extra_tables = [t for t in tables if t not in expected_models]
    if extra_tables:
        print(f"\n⚠ Tabelas extras encontradas: {extra_tables}")

def detailed_table_inspection(tables):
    """Inspeção detalhada de cada tabela"""
    print_header("4. INSPEÇÃO DETALHADA DAS TABELAS")
    
    for table in sorted(tables):
        try:
            check_table_structure(table)
            check_table_data(table)
        except Exception as e:
            print(f"  ✗ Erro ao inspecionar {table}: {e}")

def check_relationships():
    """Verifica integridade de relacionamentos"""
    print_header("5. INTEGRIDADE DE RELACIONAMENTOS")
    
    try:
        # Verificar se há tasks órfãs (sem usuário)
        orphaned_tasks = db.session.execute(db.text("""
            SELECT COUNT(*) FROM task 
            WHERE user_id NOT IN (SELECT id FROM user)
        """)).scalar()
        
        if orphaned_tasks == 0:
            print("✓ Nenhuma tarefa órfã encontrada")
        else:
            print(f"✗ {orphaned_tasks} tarefas órfãs encontradas!")
        
        # Contar usuários e tarefas
        user_count = db.session.query(User).count()
        task_count = db.session.query(Task).count()
        
        print(f"\n  Usuários: {user_count}")
        print(f"  Tarefas: {task_count}")
        
        if user_count > 0:
            avg_tasks = task_count / user_count
            print(f"  Média de tarefas por usuário: {avg_tasks:.2f}")
        
    except Exception as e:
        print(f"✗ Erro ao verificar relacionamentos: {e}")

def check_data_integrity():
    """Verifica integridade dos dados"""
    print_header("6. INTEGRIDADE DOS DADOS")
    
    try:
        # Verificar usernames duplicados
        from sqlalchemy import func
        duplicates = db.session.execute(db.text("""
            SELECT username, COUNT(*) as count FROM user 
            GROUP BY username HAVING count > 1
        """)).fetchall()
        
        if not duplicates:
            print("✓ Nenhum username duplicado")
        else:
            print(f"✗ {len(duplicates)} usernames duplicados encontrados:")
            for dup in duplicates:
                print(f"    - {dup[0]}: {dup[1]} vezes")
        
        # Verificar senhas nulas
        null_passwords = db.session.execute(db.text("""
            SELECT COUNT(*) FROM user WHERE password IS NULL OR password = ''
        """)).scalar()
        
        if null_passwords == 0:
            print("✓ Nenhuma senha nula ou vazia")
        else:
            print(f"✗ {null_passwords} usuários com senha nula/vazia!")
        
        # Verificar tarefas sem conteúdo
        null_tasks = db.session.execute(db.text("""
            SELECT COUNT(*) FROM task WHERE content IS NULL OR content = ''
        """)).scalar()
        
        if null_tasks == 0:
            print("✓ Nenhuma tarefa sem conteúdo")
        else:
            print(f"✗ {null_tasks} tarefas sem conteúdo!")
            
    except Exception as e:
        print(f"✗ Erro ao verificar integridade: {e}")

def main():
    """Executa varredura completa"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "VARREDURA COMPLETA DO BANCO DE DADOS" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    
    with app.app_context():
        # 1. Verificar se banco existe
        if not check_database_status():
            print("\n✗ Banco de dados não encontrado!")
            return 1
        
        # 2. Listar tabelas
        tables = list_all_tables()
        
        # 3. Validar modelos vs tabelas
        validate_models_vs_tables(tables)
        
        # 4. Inspeção detalhada
        if tables:
            detailed_table_inspection(tables)
        
        # 5. Verificar relacionamentos
        if 'user' in tables and 'task' in tables:
            check_relationships()
        
        # 6. Verificar integridade
        if 'user' in tables:
            check_data_integrity()
        
        # Resumo final
        print_header("RESUMO FINAL")
        if tables:
            print(f"✓ Banco de dados sincronizado com {len(tables)} tabela(s)")
            print("✓ Você pode iniciar a aplicação")
            return 0
        else:
            print("✗ Nenhuma tabela encontrada - banco pode estar vazio")
            print("  Execute: python create_db.py")
            return 1

if __name__ == '__main__':
    sys.exit(main())
