# Minzai プロジェクト ChatGPT 会話まとめ

## 1. プロジェクト概要
Flask + SQLAlchemy を使用した在庫管理アプリケーション。  
機能:
- 商品登録（ジャンル・在庫・画像）
- 在庫入庫・出庫
- 在庫履歴表示
- 商品削除
- 画像アップロード

---

## 2. 使用ライブラリ
- Flask
- Flask_SQLAlchemy
- werkzeug (secure_filename)

---

## 3. ディレクトリ構成例
Minzai/
├─ app.py
├─ models.py
├─ database.py
├─ static/
│ └─ uploads/
├─ templates/
│ ├─ top.html
│ ├─ in.html
│ ├─ out.html
│ ├─ register.html
│ ├─ delete.html
│ ├─ stock.html
│ ├─ history.html
│ └─ edit.html
└─ README.md


---

## 4. データベースモデル (`models.py`)
```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    items = db.relationship('Item', backref='genre')

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)
    stock = db.relationship('Stock', uselist=False, backref='item')
    histories = db.relationship('StockHistory', backref='item', lazy=True)
    file = db.Column(db.String(200))  # 画像ファイル名

class Stock(db.Model):
    __tablename__ = 'stocks'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)

class StockHistory(db.Model):
    __tablename__ = 'stock_histories'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    change = db.Column(db.Integer, nullable=False)
    memo = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)

5. データベース作成 (database.py)
from app import app
from models import db

with app.app_context():
    db.create_all()
    print("minazai.db とテーブルを作成しました")


カラム追加の場合：

from app import app
from models import db

with app.app_context():
    conn = db.engine.connect()
    conn.execute("ALTER TABLE items ADD COLUMN file TEXT;")
    print("fileカラムを追加しました")
    conn.close()

6. 画像アップロードの設定 (app.py)
import os
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 画像保存処理
if file and file.filename:
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)  # フォルダがなければ作成
    file.save(save_path)

7. Git 共有の注意点

プロジェクトを zip にして別PCにコピーしても動作可能

ただし、venv は含めず、必要なライブラリは requirements.txt で管理

.gitignore に *.db や __pycache__/ を追加するのがおすすめ

8. 備考

Flaskの app.config['UPLOAD_FOLDER'] に指定したディレクトリが存在しない場合、画像保存時にエラーが発生する

os.makedirs() で自動生成すると安全

データベースに新しいカラムを追加した場合は、既存のDBには ALTER TABLE で反映が必要


---

これを **そのまま `README.md`** として保存すれば、別PCでも見やすくなりますし、GitHubに載せるときも便利です。

---

希望なら、この中に **これまでのやり取りの補足コメントや問題解決手順も含めた完全版** にすることもできます。  

作ってほしいですか？