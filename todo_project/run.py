import os
from todo_project import app, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    app.run(host=host, port=5000, debug=True)
