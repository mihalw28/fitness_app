from app import create_app, db
from app.models import User, Train
from datetime import datetime


app = create_app()
application = app

if __name__ == "__main__":
    app.run()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Train': Train}


@app.context_processor
def add_now():
    return {'now': datetime.now()}
