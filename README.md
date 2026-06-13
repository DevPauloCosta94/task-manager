# Task-Manager-using-Flask

A simple web application to store your To-Do Tasks .

# Features

- User Authentication
- Easy to use and deploy locally.

# Requirements

Execute the following command to install the required third party libraries:

```pip3 install -r requirements.txt```

# Usage

1. Clone the repository using the following command
    
    ```git clone https://github.com/AdityaBagad/Task-Manager-using-Flask.git```

2. Install the dependencies using

    ```cd  Task-Manager-using-Flask```
    
    ```pip3 install -r requirements.txt```

3. Run this command to start the application

    ```cd todo_project```

    ```python run.py```

# Docker container deployment

1. Build and start the full stack with Docker Compose:

    ```docker compose up --build -d```

2. Open the services in your browser:

    - App: http://localhost:5000
    - Prometheus: http://localhost:9090
    - Grafana: http://localhost:3000 (default user: admin / password: admin)

3. The Prometheus datasource is auto-provisioned for Grafana to use the local Prometheus service.

4. Check application metrics at:

    - http://localhost:5000/metrics

5. If you want to stop the containers:

    ```docker compose down```

# GitHub Actions

O projeto já está alinhado para uso com GitHub Actions.
O workflow está em `.github/workflows/python-app.yml` e executa:

- checkout do repositório
- instalação de dependências Python
- verificação de sintaxe
- execução de testes unitários
- análise SAST com Bandit
- build da imagem Docker

> Obs: o arquivo `.gitlab-ci.yml` permanece no projeto, mas o fluxo principal de CI/CD para GitHub está no diretório `.github/workflows`.

# Results

## Registration Page
Login or Register if you dont have an account

![Registration Page](output/register.jpg)

## Accessing URL's 
User cannot access any URL's if they are not logged in

![Invalid Access](output/invalid-access.jpg)

## After Successfull Login
See all your tasks after successfull login.

![After Login](output/after-login.jpg)

## Add Tasks
Click the **Add Task** link in the side-bar to add tasks

![Image of Yaktocat](output/add-task.jpg)

## View All Tasks
Click the **View All Task** link in the side-bar to see all tasks. You can **Update** and **Delete** Tasks from this page.

![Image of Yaktocat](output/all-tasks.jpg)

## Account Settings
Change your username and password. You can access this by clicking dropdown in the Navbar

![Image of Yaktocat](output/account-settings.jpg)

