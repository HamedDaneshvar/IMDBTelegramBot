from pymongo import MongoClient


HOST = "mongo-bot-db"
PORT = 27017
DB_NAME = 'telegrambot'
COLLECTION_NAMES = (
    "users_lang",
    "trailers",
    "media_detail",
    "TMDB_media_detail",
)


def get_database():
    # Connect to the MongoDB container
    client = MongoClient(host=HOST, port=PORT)

    # create a db if not exist
    if DB_NAME not in client.list_database_names():
        db = client[DB_NAME]
        print("Database created:", DB_NAME)
    else:
        db = client[DB_NAME]
        print("Database already exists:", DB_NAME)

    return db


def create_collection(db, collection_names):
    for collection in collection_names:
        # create a collection if not exist
        if collection not in db.list_collection_names():
            collection = db[collection]
            print("Collection created:", collection)
        else:
            collection = db[collection]
            print("Collection already exists:", collection)


def get_collection(db, collection_name):
    return db[collection_name]


db = get_database()
create_collection(db, COLLECTION_NAMES)
users_lang_clt = get_collection(db, COLLECTION_NAMES[0])
trailers_clt = get_collection(db, COLLECTION_NAMES[1])
media_detail_clt = get_collection(db, COLLECTION_NAMES[2])
TMDB_media_detail_clt = get_collection(db, COLLECTION_NAMES[3])
