from flask import Flask, jsonify, request
from pymongo import MongoClient
import requests
import os

app = Flask(__name__)

# MongoDB connection
mongo_host = os.getenv("MONGO_HOST", "localhost")
user_service_host = os.getenv("USER_SERVICE_HOST", "localhost")
user_service_port = os.getenv("USER_SERVICE_PORT", "5001")

client = MongoClient(f"mongodb://{mongo_host}:27017/")
db = client["taskmanager"]
tasks_collection = db["tasks"]


@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = list(tasks_collection.find({}, {"_id": 0}))
    return jsonify(tasks)


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = tasks_collection.find_one({"id": task_id}, {"_id": 0})

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task)


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    last_task = tasks_collection.find_one(
        sort=[("id", -1)]
    )

    new_id = 1 if last_task is None else last_task["id"] + 1

    new_task = {
        "id": new_id,
        "title": data["title"],
        "completed": False
    }

    if "user_id" in data:
        new_task["user_id"] = data["user_id"]

    tasks_collection.insert_one(new_task)

    new_task.pop("_id", None)

    return jsonify(new_task), 201


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    result = tasks_collection.delete_one({"id": task_id})

    if result.deleted_count == 0:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"message": "Task deleted"})


@app.route("/tasks/<int:task_id>/user", methods=["GET"])
def get_task_user(task_id):
    task = tasks_collection.find_one({"id": task_id}, {"_id": 0})

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    if "user_id" not in task:
        return jsonify({"error": "Task has no user_id"}), 400

    user_url = (
        f"http://{user_service_host}:{user_service_port}"
        f"/users/{task['user_id']}"
    )

    try:
        response = requests.get(user_url, timeout=5)

        if response.status_code == 404:
            return jsonify({"error": "User not found"}), 404

        response.raise_for_status()

        return jsonify(response.json())

    except requests.RequestException:
        return jsonify({
            "error": "User Service unavailable"
        }), 503


@app.route("/health", methods=["GET"])
def health():
    try:
        client.admin.command("ping")

        return jsonify({
            "status": "healthy",
            "database": "connected"
        })

    except Exception:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected"
        }), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)