from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'postgresql://myuser:mypassword@localhost:5432/tictactoe'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)