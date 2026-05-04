#Flask app factory, database set up via models.init_db()

import os
import time
import threading
from flask import Flask
from models.models import init_db


def create_app(config_overrides: dict = None) -> Flask:
    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="static",
    )

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "tales-of-time-dev-key")

    if config_overrides:
        app.config.update(config_overrides)

    init_db()

    from views.views import bp
    app.register_blueprint(bp)

    from backup import backup_sqlite_db

    def backup_loop():
        app.app_context().push()
        while True:
            time.sleep(60 * 60)
            backup_sqlite_db()

    threading.Thread(target=backup_loop, daemon=True).start()

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
