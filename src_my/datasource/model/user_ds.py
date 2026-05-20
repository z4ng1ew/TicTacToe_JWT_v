from datasource.database import db


class UserDS(db.Model): 
    __tablename__ = 'users' 
    id: str = db.Column(db.String(36), primary_key=True)
    login: str = db.Column(db.String(64), nullable=False, unique=True)
    password_hash: str = db.Column(db.String(256), nullable=False)
    def __repr__(self) -> str:
        return f'<UserDS id={self.id} login={self.login}>'