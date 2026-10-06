from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from config import Config
from extensions import cors, init_db, jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    Config.INDEX_DIR.mkdir(parents=True, exist_ok=True)

    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    jwt.init_app(app)
    init_db(app)

    from routes.auth import bp as auth_bp
    from routes.chat import bp as chat_bp
    from routes.reports import bp as reports_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(chat_bp, url_prefix="/api/reports")

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", llm=bool(app.config["GROQ_API_KEY"]))

    @app.errorhandler(HTTPException)
    def http_error(e):
        return jsonify(error=e.description), e.code

    @app.errorhandler(Exception)
    def server_error(e):
        app.logger.exception(e)
        return jsonify(error="Internal server error"), 500

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
