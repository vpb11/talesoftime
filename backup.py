import sqlite3
import os
from datetime import datetime
from flask import current_app


def backup_sqlite_db():
    #timestamped backup using the native SQLite backup API
    db_path = os.path.join(current_app.instance_path, 'tales_of_time.db')
    backup_dir = os.path.join(current_app.instance_path, 'backups')

    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'talesoftime_backup_{timestamp}.db')

    try:
        source = sqlite3.connect(db_path)
        dest = sqlite3.connect(backup_path)

        with dest:
            source.backup(dest)

        source.close()
        dest.close()

        print(f"SUCCESS: Backup created at {backup_path}")
        return backup_path
    except Exception as e:
        print(f"FAILED: Backup error: {str(e)}")
        return None


#runs as a standalone script with a Flask context
if __name__ == "__main__":
    try:
        from app import create_app

        flask_app = create_app()
        with flask_app.app_context():
            print("Starting automated backup process...")
            result = backup_sqlite_db()
            if result:
                print("Process completed successfully.")
            else:
                print("Process failed.")

    except ImportError:
        print("ERR, Could not find 'app.py'.")
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
