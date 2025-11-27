from app import app
from models import db
from sqlalchemy import text  # ← これをインポート

with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(text("ALTER TABLE items ADD COLUMN file TEXT;"))
        conn.commit()
    print("itemsテーブルに file カラムを追加しました")
