import os
import logging
from logging.handlers import SysLogHandler
import json as _json

from flask import Flask
# Compatibilidade: algumas bibliotecas esperam `flask.Markup` ou `jinja2.Markup` (removidos em releases recentes).
# Se não existirem, mapeamos para `markupsafe.Markup` antes de carregar extensões.
try:
    from markupsafe import Markup as _Markup  # type: ignore
    import flask as _flask
    if not hasattr(_flask, 'Markup'):
        setattr(_flask, 'Markup', _Markup)
    try:
        import jinja2 as _jinja2
        if not hasattr(_jinja2, 'Markup'):
            setattr(_jinja2, 'Markup', _Markup)
    except Exception:
        pass
except Exception:
    pass

# Compatibilidade: Flask-WTF (versão 0.14.x) espera `flask.json.JSONEncoder`,
# que foi removido em Flask 2.2+. Injetamos o `json.JSONEncoder` padrão.
try:
    import flask.json as _fjson
    if not hasattr(_fjson, 'JSONEncoder'):
        setattr(_fjson, 'JSONEncoder', _json.JSONEncoder)
except Exception:
    pass

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
# Compatibilidade: alguns releases do Werkzeug removeram `safe_str_cmp`.
# Se estiver ausente, injetamos uma implementação segura baseada em hmac
# antes de importar `Flask-Bcrypt`, que importa `safe_str_cmp`.
try:
    from werkzeug.security import safe_str_cmp  # type: ignore
except Exception:
    import hmac

    def safe_str_cmp(a, b):
        try:
            return hmac.compare_digest(str(a), str(b))
        except Exception:
            return False

    import werkzeug.security as _ws
    setattr(_ws, 'safe_str_cmp', safe_str_cmp)

from flask_bcrypt import Bcrypt
from prometheus_client import Counter

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '45cf93c4d41348cd9980674ade9a7356')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SYSLOG_ADDRESS'] = os.environ.get('SYSLOG_ADDRESS', '/dev/log')

# Logging configuration
formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
try:
    if app.config['SYSLOG_ADDRESS'].startswith('/'):
        handler = SysLogHandler(address=app.config['SYSLOG_ADDRESS'])
    else:
        syslog_host, syslog_port = app.config['SYSLOG_ADDRESS'].split(':')
        handler = SysLogHandler(address=(syslog_host, int(syslog_port)))
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
except Exception:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    app.logger.addHandler(console_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Application starting')


db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'danger'

bcrypt = Bcrypt(app)

# Prometheus metrics
login_success = Counter('task_manager_login_success_total', 'Successful login attempts')
login_failure = Counter('task_manager_login_failure_total', 'Failed login attempts')
task_created = Counter('task_manager_tasks_created_total', 'Tasks created')
task_deleted = Counter('task_manager_tasks_deleted_total', 'Tasks deleted')
user_registered = Counter('task_manager_user_registered_total', 'Registered users')
request_count = Counter('task_manager_requests_total', 'Request count', ['method', 'endpoint', 'status'])

# Always put Routes at end
from todo_project import routes