from datetime import datetime, timezone

import bcrypt
from bson import ObjectId

from database import users_collection


class UserModel:
    def __init__(self, data: dict):
        self.data = data

    @property
    def _id(self):
        return self.data.get('_id')

    @property
    def password_hash(self):
        return self.data.get('password_hash', '')

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def _int_credits(value) -> int:
        return int(value)

    @classmethod
    def create_user(cls, name: str, email: str, password: str):
        user_doc = {
            'name': name,
            'email': email.lower().strip(),
            'password_hash': cls._hash_password(password),
            'credits': cls._int_credits(10),
            'created_tasks': [],
            'accepted_tasks': [],
            'created_at': datetime.now(timezone.utc),
        }
        result = users_collection.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        return cls(user_doc)

    @classmethod
    def find_user_by_email(cls, email: str):
        user_doc = users_collection.find_one({'email': email.lower().strip()})
        return cls(user_doc) if user_doc else None

    def verify_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8'),
        )

    @classmethod
    def update_credits(cls, user_id, amount: int):
        oid = ObjectId(user_id) if isinstance(user_id, str) else user_id
        users_collection.update_one(
            {'_id': oid},
            {'$inc': {'credits': cls._int_credits(amount)}},
        )
        updated = users_collection.find_one({'_id': oid})
        return cls(updated) if updated else None
