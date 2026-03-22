from pymongo import MongoClient

from config import Config


def main() -> None:
    uri = Config.MONGO_URI
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)

    # Force a real connection attempt.
    client.admin.command("ping")

    db = client["timebank"]

    print("Connected to MongoDB")
    print(db.list_collection_names())


if __name__ == "__main__":
    main()
