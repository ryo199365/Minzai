import os
from flask import Flask,render_template,request
from models import db,Genre,Item,Stock,StockHistory
from werkzeug.utils import secure_filename

# Flask アプリ作成
app = Flask(__name__)
# DB 設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///minazai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# アップロード先フォルダの設定
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# DBをFlaskアプリに紐づける
db.init_app(app)

@app.route('/')
def top():
    return render_template('top.html') 
 # templateフォルダ内のtop.htmlを表示

@app.route('/in' , methods=['GET','POST'])
def stock_in() : 
    # GET,POSTでもDBから全アイテムを取得(Itemとstockを結合して在庫数も取得)
    items = db.session.query(Item,Stock).join(Stock).all()
    
    if request.method == 'POST':
        # フォームから送られてきたデータを取得
        item_id = int(request.form['item.id'])
        add_quantity = int(request.form['quantity'])
    # テンプレートに渡す
    return render_template('in.html')
# templateフォルダ内のin.htmlを表示



@app.route('/out')
def stock_out() : return render_template('out.html')
# templateフォルダ内のout.htmlを表示

@app.route('/register' , methods=['GET','POST'])
def register():
    # フォームが送信されたとき(POSTメソッド)のときの処理
    # POSTなら「フォームの入力値を受け取って処理する」
    if request.method == 'POST':
        # HTML側の <input> や <select> の name="" に対応してる。
        item_name = request.form['item_name']
        item_genre = request.form['item_genre']
        new_genre = request.form['new_genre']
        quantity = int(request.form['quantity'])
        file = request.files['item_file']
        # 新しいジャンルが入力されていた場合
        if new_genre:
            genre = Genre(name=new_genre)
            db.session.add(genre)
            # DBに保存してIDを確定
            db.session.commit()
        # 既存ジャンルを選択した場合
        else :
            genre = Genre.query.filter_by(name=item_genre).first()
        # 🟢 ジャンルが見つからない場合の安全処理
        if not genre:
            return "ジャンルが見つかりませんでした。", 400
        # 商品登録(genre_idと紐づけ)
        item = Item(name=item_name,genre_id=genre.id)
        db.session.add(item)
        db.session.commit()    
        # 在庫登録(stockテーブルへ)
        stock = Stock(item_id=item.id,quantity=quantity)
        db.session.add(stock)
        db.session.commit()
        # 画像ファイル追加
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("ファイルがアップロードされました:", filename)
         # ここで保存やDB登録をする
         # 確認用に出力（後でDB登録などに変更予定）
        print("アイテム名:", item_name)
        print("ジャンル:", item_genre)
        print("在庫数:", quantity)
        print("ファイル:", file.filename if file else "なし")
        

        # POST後も同じページを表示
        return render_template('register.html')
      
    #GETのときもテンプレートを返す
    # GETなら「空の登録画面」を表示するだけ。
    return render_template('register.html')
# templateフォルダ内のregister.htmlを表示

    



@app.route('/delete')
def delete() : return render_template('delete.html')
# templateフォルダ内のdelete.htmlを表示

@app.route('/history')
def history() : return render_template('history.html')
# templateフォルダ内のhistory.htmlを表示

@app.route('/stock')
def stock() : return render_template('stock.html')
print('現在の在庫状況')

# templateフォルダ内のstock.htmlを表示

@app.route('/edit')
def edit() : return render_template('edit.html')
# templateフォルダ内のstock.htmlを表示


if __name__ == '__main__' : app.run(debug=True,port=5001)

