import os
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify
from sqlalchemy import text

from extensions import db


def response(code: int, message: str, data: Any = None):
    return jsonify({"code": code, "message": message, "data": data}), code


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False

    load_dotenv()

    if test_config is not None:
        app.config.update(test_config)
    else:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise RuntimeError(
                "未設定環境變數 DATABASE_URL。請在 .env 或環境變數中設定 PostgreSQL 連線字串。"
            )
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    db.init_app(app)

    @app.get("/api/health")
    def health():
        return response(
            200,
            "伺服器運作正常，測試正常可以進行其他任務。",
            {
                "status": "ok",
                "time": datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.get("/api/health/db")
    def health_db():
        try:
            db.session.execute(text("SELECT 1"))
            return response(200, "資料庫連線正常", {"status": "ok"})
        except Exception as error:
            db.session.rollback()
            app.logger.error("資料庫連線失敗: %s", error)
            return response(500, "資料庫暫時連不上", None)

    @app.errorhandler(404)
    def handle_not_found(_error):
        return response(404, "找不到這一筆", None)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
