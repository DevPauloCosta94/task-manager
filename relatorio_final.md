# Relatório Final do Estudo de Caso

## 1. Introdução

Este documento descreve o trabalho final do curso Hackerdogem para a implementação e containerização de um sistema de gerenciamento de tarefas pessoais. O objetivo foi adaptar a aplicação existente para rodar em containers Docker, incluir monitoramento com Prometheus e Grafana, e documentar o pipeline de CI/CD solicitado.

## 2. Objetivos do estudo de caso

O objetivo deste relatório é apresentar a execução do cenário solicitado no `casodeuso.md`, incluindo:
- identificação dos requisitos e arquitetura da solução;
- containerização da aplicação Flask;
- inclusão de monitoramento com Prometheus e Grafana;
- registro do pipeline CI/CD básico com SAST;
- sugestão de prints apropriados para cada etapa do caso de uso.

## 3. Etapa 1: Análise de requisitos e arquitetura

### 3.1 Requisitos relevantes identificados

A partir do `casodeuso.md`, os requisitos mais importantes para este trabalho são:
- autenticação obrigatória antes de acesso às funcionalidades;
- geração de logs de atividades e falhas de autenticação;
- execução em container Docker;
- monitoramento pós-implantação com Prometheus e Grafana.

### 3.2 Observações sobre o repositório original

O repositório contém:
- `todo_project/`: aplicação Flask completa com autenticação, CRUD de tarefas e templates Bootstrap;
- `task-manager/`: app de teste simples que não é utilizado no fluxo principal de containerização.

Comentário: o foco do projeto final deve ser `todo_project/`, pois é o app funcional que atende aos requisitos de tarefas e autenticação.

### 3.3 Sugestão de print para etapa 1

- Print 1: estrutura do projeto no VS Code mostrando `todo_project/`, `docker-compose.yml` e `prometheus/prometheus.yml`.

## 4. Etapa 2: Desenvolvimento e containerização

### 4.1 Ajustes no código

Foram realizados os seguintes ajustes no código para suportar o ambiente em container:
- adicionada exportação de métricas no endpoint `/metrics`;
- criados contadores Prometheus para eventos de login, registro e manipulação de tarefas;
- adicionada configuração de logging com fallback para console quando syslog não estiver disponível.

### 4.2 Ajustes na containerização

O `Dockerfile` e `docker-compose.yml` foram atualizados para:
- usar `python:3.11-slim` e `gunicorn` como servidor de produção leve;
- copiar o conteúdo de `todo_project/` para `/app` no container;
- expor a aplicação em `5000`, Prometheus em `9090` e Grafana em `3000`;
- provisionar automaticamente o datasource Prometheus no Grafana.

### 4.3 Resultados desta etapa

Com esses ajustes, a aplicação passa a atender ao requisito de containerização e monitoração. A versão ajustada do app pode ser iniciada com:

- `docker compose up --build -d`

### 4.4 Sugestões de prints para etapa 2

- Print 2: `docker compose up --build -d` em execução no terminal.
- Print 3: tela inicial do app (`http://localhost:5000`).
- Print 4: página de login/registro.

## 5. Etapa 3: Pipeline CI/CD

### 5.1 Objetivo do pipeline

O `casodeuso.md` exige um pipeline que valide o ambiente a cada commit, incluindo build, testes e análise estática de segurança.

### 5.2 Implementação proposta

O arquivo `.gitlab-ci.yml` foi criado com as seguintes etapas:
- `lint`: validação básica de Python e compilação do arquivo principal;
- `build`: construção da imagem Docker do app;
- `test`: execução de testes automatizados (padrão `unittest`);
- `sast`: análise de segurança estática com Bandit;
- `deploy`: etapa manual placeholder para ambiente de stage/produção.

### 5.3 Sugestão de print para etapa 3

- Print 5: conteúdo do arquivo `.gitlab-ci.yml` aberto no editor.
- Print 6: saída de validação local do pipeline ou comando `python -m py_compile todo_project/run.py`.

## 6. Etapa 4: Análise estática de código (SAST)

### 6.1 Ferramentas e execução

Para SAST, foi sugerido o uso de Bandit. A etapa do pipeline instala Bandit e executa:

- `bandit -r todo_project`

Comentário: se houver vulnerabilidades, o próximo passo é corrigir o código e repetir a análise.

### 6.2 Sugestão de print para etapa 4

- Print 7: resultado da execução local do `bandit -r todo_project`.

## 7. Etapa 5: Monitoramento pós-implantação

### 7.1 Prometheus

O Prometheus está configurado em `prometheus/prometheus.yml` para coletar métricas do serviço `task-manager:5000`.

### 7.2 Grafana

O Grafana foi provisionado automaticamente com o datasource Prometheus em:
- `grafana/provisioning/datasources/datasource.yml`

### 7.3 Métricas expostas

Métricas relevantes disponíveis:
- `task_manager_login_success_total`
- `task_manager_login_failure_total`
- `task_manager_tasks_created_total`
- `task_manager_tasks_deleted_total`
- `task_manager_user_registered_total`
- `task_manager_requests_total`

### 7.4 Sugestão de print para etapa 5

- Print 8: página de targets do Prometheus (`http://localhost:9090/targets`).
- Print 9: navegador exibindo métricas em `http://localhost:5000/metrics`.
- Print 10: dashboard Grafana com pelo menos dois painéis de métricas.

## 8. Roteiro prático para execução e prints

### 8.1 Passo a passo

1. Abra o terminal na pasta do projeto.
2. Inicie os containers:
   - `docker compose up --build -d`
3. Verifique o estado dos serviços:
   - `docker compose ps`
4. Acesse os serviços no navegador:
   - App: `http://localhost:5000`
   - Prometheus: `http://localhost:9090`
   - Grafana: `http://localhost:3000`
5. Acesse as métricas:
   - `http://localhost:5000/metrics`

### 8.2 Exemplos de prints por etapa

- Estrutura do projeto e arquivos principais.
- Execução do Docker Compose.
- Tela de login / registro da aplicação.
- Tela de lista de tarefas.
- Prometheus targets.
- Métricas expostas em `/metrics`.
- Dashboard Grafana com gráficos de login e tarefas.
- Resultado da análise Bandit.

## 9. Observações de segurança e melhorias

### 9.1 Segurança implementada

- autenticação obrigatória para funcionalidades de tarefas;
- hashing de senha com BCrypt;
- logs de evento registrados para sucessos e falhas de login.

### 9.2 Melhorias sugeridas

- integrar OWASP ZAP para DAST, como indicado no `casodeuso.md`;
- adicionar análise de dependências com `pip-audit` ou `safety`;
- trocar senha padrão do Grafana antes de entregar em ambiente real;
- configurar rotas de logout e proteção adicional de CSRF se necessário.

## 10. Conclusão

O relatório final agora alinha as principais etapas do `casodeuso.md` com comentários e sugestões de prints. Ele descreve o que foi adaptado e como validar cada fase do trabalho, fornecendo um roteiro claro para entregar em até 5-7 páginas.

> Para gerar o PDF final, converta este arquivo Markdown (`relatorio_final.md`) para PDF usando um editor ou ferramenta como `pandoc`.
