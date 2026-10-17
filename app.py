from datetime import datetime, timezone
from typing import Any

from flask import Flask, jsonify, request


app = Flask(__name__)
app.json.ensure_ascii = False

tasks: list[dict[str, Any]] = [
    {
        "id": 1,
        "title": "完成 Flask API",
        "description": "建立任務管理系統的基本端點。",
    },
    {
        "id": 2,
        "title": "撰寫 API 測試",
        "description": "驗證各端點的成功與錯誤回應。",
    },
]


def response(
    status: str, message: str, data: Any, status_code: int
):
    return jsonify({"status": status, "message": message, "data": data}), status_code


@app.get("/api/health")
def health():
    return response(
        "success",
        "Server is running",
        {"status": "running", "timestamp": datetime.now(timezone.utc).isoformat()},
        200,
    )


@app.get("/api/tasks")
def get_tasks():
    return response("success", "Tasks retrieved successfully", tasks, 200)


@app.post("/api/tasks")
def create_task():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return response("error", "Request body must be valid JSON", None, 400)

    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        return response("error", "The title field is required", None, 400)

    description = payload.get("description", "")
    if description is None:
        description = ""

    task = {
        "id": max((task["id"] for task in tasks), default=0) + 1,
        "title": title.strip(),
        "description": description,
    }
    tasks.append(task)

    return response("success", "Task created successfully", task, 201)


@app.get("/api/tasks/<int:task_id>")
def get_task(task_id: int):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if task is None:
        return response("error", "Task not found", None, 404)

    return response("success", "Task retrieved successfully", task, 200)


@app.errorhandler(404)
def handle_not_found(_error):
    return response("error", "Resource not found", None, 404)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
