import os

from flask import Flask, jsonify
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.environ.get("MONGO_DB", "tp1")

app = Flask(__name__)
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
db = client[MONGO_DB]


@app.route("/")
def hello_world():
	return "Hello, World!"


@app.route("/health")
def health():
	try:
		client.admin.command("ping")
	except PyMongoError as e:
		return jsonify(status="error", mongo=str(e)), 503
	return jsonify(status="ok", mongo="connected")


@app.route("/visits")
def visits():
	counter = db.counters.find_one_and_update(
		{"_id": "visits"},
		{"$inc": {"count": 1}},
		upsert=True,
		return_document=ReturnDocument.AFTER,
	)
	return jsonify(visits=counter["count"])


if __name__ == "__main__":
	app.run(debug=True)
