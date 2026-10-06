from flask_cors import CORS
from flask_jwt_extended import JWTManager

jwt = JWTManager()
cors = CORS()


def init_db(app):
    """Attach a MongoDB database handle to app.db."""
    uri = app.config["MONGO_URI"]
    if app.config["USE_MOCK_DB"] or not uri:
        import mongomock

        print("[ragnosis] WARNING: using in-memory mock database (data is lost on restart).")
        client = mongomock.MongoClient()
    else:
        import certifi
        from pymongo import MongoClient

        client = MongoClient(uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=8000)
    app.db = client[app.config["MONGO_DB"]]
    app.db.users.create_index("email", unique=True)
