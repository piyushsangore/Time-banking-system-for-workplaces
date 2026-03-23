import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    MONGO_URI = os.getenv(
        'MONGO_URI',
        'YOUR_MONGO_URI',
    )
