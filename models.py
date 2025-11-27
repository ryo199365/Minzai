from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# DBインスタンスを作成（Flaskアプリで init_app() する）
db = SQLAlchemy()
# SQLAlchemy（Flask用のORM）を使って、Pythonクラスをデータベースのテーブルとして扱えるようにしています。
# ORM = 「オブジェクトとDBテーブルを対応させる仕組み」です。

#Genre(ジャンルテーブル)
# テーブル定義
class Genre(db.Model):
    __tablename__ = 'genres'
    # カラム（列）の定義
    id = db.Column(db.Integer,primary_key=True)
    # id は主キー（自動連番）
    name = db.Column(db.String(50),unique=True)
    # name はジャンル名（重複禁止(unique=True))
    
    # リレーション（関連）
    # tems = db.relationship('Item', backref='genre') によって「ジャンル → 商品」を1対多で結びつけ
    items = db.relationship('Item',backref='genre')
    
# ------------------------------------------------------------

# Item(商品テーブル)
class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    # genre_idでジャンルと紐づけ（db.ForeginKey('genre.id')外部キー)
    # # nullable=False(nullを許可しない)
    genre_id = db.Column(db.Integer,db.ForeignKey('genres.id'),nullable=False)
        
    # 説明用の文字列列（任意）。
    description = db.Column(db.String(200))
    # 作成日時を記録。デフォルトは現在日時。
    created_at = db.Column(db.DateTime,default=datetime.now)
    
    file = db.Column(db.String(200))  # ← 画像ファイル名を保存するカラム
    
    stock = db.relationship('Stock',uselist=False,backref='item')
    # 「アイテム → 在庫」 の 1対1 関係。
    # uselist=False は「1つのアイテムにつき1つの在庫情報」という意味。
    # backref='item' によって Stock 側からも .item でアクセスできる。
    histories = db.relationship('StockHistory',backref='item',lazy=True)
    # Item → StockHistory の 1対多 関係。
    #lazy=True → 関連レコードを必要なときに読み込む。
    #StockHistory 側から .item で親のアイテムにアクセス可能。
    
    # ------------------------------------------------------------
    
    #Stock(在庫テーブル)（現在の残高）
class Stock(db.Model):
    __tablename__ = 'stocks'
    id = db.Column(db.Integer,primary_key=True)
    # → items テーブルの id を参照する外部キー。
    #→ unique=True によって 1つのアイテムにつき1行だけ（＝1対1の関係）を保証しています。
    #→ nullable=False により必須項目です（在庫は必ずどれかのアイテムに紐づく）。
    item_id = db.Column(db.Integer,db.ForeignKey('items.id'),unique=True,nullable=False)
    
    #  実際の在庫数。デフォルト 0、NULL を許容しない設定。
    quantity = db.Column(db.Integer,default=0,nullable=False)
    
    # ------------------------------------------------------------
        
    #StockHistory(在庫履歴テーブル)（入出庫記録）
class StockHistory(db.Model):
    __tablename__ = 'stock_histories'
    id = db.Column(db.Integer,primary_key=True)
    item_id = db.Column(db.Integer,db.ForeignKey('items.id'),nullable=False)
    #change → 数量の増減（入庫 +10、出庫 −3 など）
    change = db.Column(db.Integer,nullable=False) #入庫は+、出庫は-
    # memo → 備考（「仕入れ」「返品処理」など）
    memo = db.Column(db.String(200))
    created_at = db.Column(db.DateTime,default=datetime.now)
        
        
    


