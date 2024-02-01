# https://dev.to/paurakhsharma/flask-rest-api-part-4-exception-handling-5c6a

import os
from flask import Flask, jsonify
from flask_smorest import Api
from src.db import db 

from src.resources.department import blp as DeptBlueprint
from src.resources.user import blp as UserBlueprint

def create_app(db_url: str | None = None):
    app = Flask(__name__)
    #load_dotenv()
    # error raised in extension to bubble up to main app
    app.config["PROPAGATE_EXCEPTIONS"] = True

    # API documentation for swagger ui: http://127.0.0.1:5000/swagger-ui
    app.config["API_TITLE"] = "Employees REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # Database config
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "duckdb:///database/database.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # to improve performance
    db.init_app(app)
    
    api = Api(app)
    
    blueprints = [DeptBlueprint, UserBlueprint]
    for bp in blueprints:
        api.register_blueprint(bp)
    return app

if __name__ == '__main__':
    create_app().run(port=5000)



# extensions

# db = SQLAlchemy()
# migrate = Migrate()
# ma = Marshmallow()