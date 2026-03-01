from app.extensions import db, bcrypt
from app.models.base_model import BaseModel

class User(BaseModel):
    __tablename__ = 'users'
    
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password = db.Column('password', db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    places = db.relationship('Place', backref='owner', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='author', lazy=True, cascade='all, delete-orphan')
    
    @property
    def password(self):
        raise AttributeError('password is not readable')
    
    @password.setter
    def password(self, plain_password):
        self._password = bcrypt.generate_password_hash(plain_password).decode('utf-8')
    
    def verify_password(self, plain_password):
        return bcrypt.check_password_hash(self._password, plain_password)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin
        })
        return base_dict
