from app import app
from models import db,Genre,Item,Stock,StockHistory

with app.app_context():db.create_all()
print("Minazai.dbとテーブルを作成した")
    