import os 

class Config: 
    SECRET_KEY="supersecretkey" 
    
    SQLALCHEMY_DATABASE_URI = "sqlite:///dataabase.db" 
    SQLALCHEMY_TRACK_MODIFICATIONS = False