from datetime import datetime

from app import create_app, db
from app.models import Train, User

app = create_app()
application = app

if __name__ == "__main__":
    application.run(host="0.0.0.0")


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Train": Train}


@app.context_processor
def add_now():
    return {"now": datetime.now()}
