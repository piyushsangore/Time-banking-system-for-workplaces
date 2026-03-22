from datetime import datetime, timezone

from bson import ObjectId

from database import tasks_collection


class TaskModel:
    @staticmethod
    def _to_object_id(value):
        return ObjectId(value) if isinstance(value, str) else value

    @classmethod
    def create_task(
        cls,
        creator_id,
        title: str,
        description: str,
        credits: int,
        duration,
        deadline: datetime,
    ):
        task_doc = {
            'creator_id': cls._to_object_id(creator_id),
            'title': title,
            'description': description,
            'credits': credits,
            'duration': duration,
            'deadline': deadline,
            'acceptor_id': None,
            'status': 'live',
            'created_at': datetime.now(timezone.utc),
        }
        result = tasks_collection.insert_one(task_doc)
        task_doc['_id'] = result.inserted_id
        return task_doc

    @staticmethod
    def get_live_tasks():
        return list(
            tasks_collection.find({'status': 'live'}).sort('created_at', -1)
        )

    @classmethod
    def accept_task(cls, task_id, acceptor_id):
        task_oid = cls._to_object_id(task_id)
        acceptor_oid = cls._to_object_id(acceptor_id)

        result = tasks_collection.update_one(
            {'_id': task_oid, 'status': 'live'},
            {
                '$set': {
                    'acceptor_id': acceptor_oid,
                    'status': 'accepted',
                }
            },
        )
        if result.modified_count == 0:
            return None
        return tasks_collection.find_one({'_id': task_oid})

    @classmethod
    def complete_task(cls, task_id):
        task_oid = cls._to_object_id(task_id)

        result = tasks_collection.update_one(
            {'_id': task_oid, 'status': 'accepted'},
            {'$set': {'status': 'completed'}},
        )
        if result.modified_count == 0:
            return None
        return tasks_collection.find_one({'_id': task_oid})

    @staticmethod
    def expire_old_tasks():
        now = datetime.now(timezone.utc)
        result = tasks_collection.update_many(
            {
                'deadline': {'$lt': now},
                'status': {'$in': ['live', 'accepted']},
            },
            {'$set': {'status': 'expired'}},
        )
        return result.modified_count
