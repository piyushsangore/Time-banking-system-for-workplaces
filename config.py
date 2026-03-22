import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    MONGO_URI = os.getenv(
        'MONGO_URI',
        'mongodb+srv://admin:admin@gps.nzfxn7s.mongodb.net/?retryWrites=true&w=majority&appName=GPS',
    )
