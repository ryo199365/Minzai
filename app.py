import os
from flask import Flask,render_template,request,redirect
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

@app.route('/in', methods=['GET', 'POST'])
def stock_in():
    # Item と Stock を結合して全アイテムの在庫を取得
    items = db.session.query(Item, Stock).join(Stock).all()

    if request.method == 'POST':
        # フォームから送信された値を取得
        item_id = int(request.form['item_id'])
        add_quantity = int(request.form['quantity'])

        # 対象アイテムの在庫を取得
        stock = Stock.query.filter_by(item_id=item_id).first()

        # 在庫数を増やす
        stock.quantity += add_quantity

        # ----------------------------
        # 入庫履歴を StockHistory に追加
        # ----------------------------
        history = StockHistory(
            item_id=item_id,
            change=add_quantity,  # 入庫はプラス
            memo="入庫"           # メモを任意で変更可能
        )
        db.session.add(history)

        # DBに反映
        db.session.commit()

        return redirect('/in')

    # GET時は在庫一覧を表示
    return render_template('in.html', items=items)



# @app.route('/in' , methods=['GET','POST'])
# def stock_in() : 
#     # GET,POSTでもDBから全アイテムを取得(Itemとstockを結合して在庫数も取得)
#     items = db.session.query(Item,Stock).join(Stock).all()
    
#     if request.method == 'POST':
#         # フォームから送られてきたデータを取得
#         item_id = int(request.form['item.id'])
#         add_quantity = int(request.form['quantity'])
#     # テンプレートに渡す
#     return render_template('in.html')
# # templateフォルダ内のin.htmlを表示



@app.route('/out', methods=['GET', 'POST'])
def stock_out():
    # 在庫一覧（Item + Stock）を取得
    items = db.session.query(Item, Stock).join(Stock).all()

    if request.method == 'POST':
        # フォームから送信された値を取得
        item_id = int(request.form['item_id'])
        out_quantity = int(request.form['quantity'])

        # 出庫対象の在庫を取得
        stock = Stock.query.filter_by(item_id=item_id).first()

        # 在庫チェック
        if stock.quantity < out_quantity:
            return "在庫が不足しています。", 400

        # 在庫を減らす
        stock.quantity -= out_quantity

        # ----------------------------
        # 出庫履歴を StockHistory に追加
        # ----------------------------
        history = StockHistory(
            item_id=item_id,
            change=-out_quantity,  # 出庫はマイナス
            memo="出庫"           # メモを適宜変更可能
        )
        db.session.add(history)   # セッションに追加

        # DBに反映
        db.session.commit()

        return redirect('/out')

    # GET時は在庫一覧を表示
    return render_template('out.html', items=items)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # ----------------------------
    # POSTリクエストの処理（フォーム送信時）
    # ----------------------------
    if request.method == 'POST':
        # ----------------------------
        # フォームから送られた値を取得
        # ----------------------------
        item_name = request.form['item_name']     # アイテム名
        item_genre = request.form['item_genre']   # プルダウンで選択された既存ジャンル
        new_genre = request.form['new_genre']     # 新規ジャンル（入力されていれば文字列）
        quantity = int(request.form['quantity'])  # 初期在庫数（整数に変換）
        file = request.files.get('item_file')     # 画像ファイル（任意）

        # ----------------------------
        # ジャンルの処理
        # ----------------------------
        # もし新規ジャンルが入力されていればそちらを優先
        genre_name = new_genre or item_genre
        # DBに同名のジャンルが存在するか検索
        genre = Genre.query.filter_by(name=genre_name).first()
        if not genre:
            # 存在しなければ新規ジャンルとしてDBに追加
            genre = Genre(name=genre_name)
            db.session.add(genre)
            db.session.commit()  # IDを確定させるためにコミット

        # ----------------------------
        # アイテム登録
        # ----------------------------
        # ItemモデルにジャンルIDを紐づけて登録
        item = Item(name=item_name, genre_id=genre.id)
        db.session.add(item)
        db.session.commit()  # IDを確定

        # ----------------------------
        # 在庫登録（Stockテーブルに初期在庫を追加）
        # ----------------------------
        stock = Stock(item_id=item.id, quantity=quantity)
        db.session.add(stock)
        db.session.commit()

        # ----------------------------
        # 画像ファイル処理（任意）
        # ----------------------------
        if file and file.filename:
            # ファイル名を安全化
            filename = secure_filename(file.filename)
            # アップロード先に保存
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("ファイルがアップロードされました:", filename)

        # ----------------------------
        # デバッグ用出力（登録内容確認用）
        # ----------------------------
        print("アイテム名:", item_name)
        print("ジャンル:", genre_name)
        print("在庫数:", quantity)
        print("ファイル:", file.filename if file else "なし")

        # ----------------------------
        # POST後はリダイレクトしてページをリロード
        # ----------------------------
        return redirect('/register')

    # ----------------------------
    # GETリクエストの処理（初回表示やリロード）
    # ----------------------------
    # DBから既存ジャンルを全件取得してテンプレートに渡す
    genres = Genre.query.all()
    # 空の登録画面を表示（プルダウンはDBジャンルから生成）
    return render_template('register.html', genres=genres)


    



@app.route('/delete', methods=['GET', 'POST'])
def delete():
    # GET: 削除するアイテム一覧を表示
    if request.method == 'GET':
        # Item と Stock を結合して在庫情報も取得
        items = db.session.query(Item, Stock).join(Stock).all()
        return render_template('delete.html', items=items)

    # POST: 削除実行
    if request.method == 'POST':
        item_id = int(request.form['item_id'])

        # 削除対象のアイテムを取得
        item = Item.query.get(item_id)
        if not item:
            return "削除対象が見つかりません", 404

        # ----------------------------
        # 関連する在庫（Stock）を削除
        # ----------------------------
        stock = Stock.query.filter_by(item_id=item_id).first()
        if stock:
            db.session.delete(stock)

        # ----------------------------
        # 関連する在庫履歴（StockHistory）を削除
        # ----------------------------
        histories = StockHistory.query.filter_by(item_id=item_id).all()
        for history in histories:
            db.session.delete(history)

        # ----------------------------
        # アイテム本体を削除
        # ----------------------------
        db.session.delete(item)

        # DBに反映
        db.session.commit()

        return redirect('/delete')


from datetime import datetime

@app.route('/history', methods=['GET'])
def history():
    # 検索・フィルター用パラメータ取得
    search_name = request.args.get('search_name', '')
    filter_genre = request.args.get('filter_genre', '')
    start_date = request.args.get('start_date', '')  # 開始日
    end_date = request.args.get('end_date', '')      # 終了日

    # StockHistory と Item と Genre を結合
    query = (
        db.session.query(
            StockHistory,
            Item.name.label('item_name'),
            Genre.name.label('genre_name')
        )
        .join(Item, StockHistory.item_id == Item.id)
        .join(Genre, Item.genre_id == Genre.id)
        .order_by(StockHistory.created_at.desc())
    )

    # アイテム名で部分一致検索
    if search_name:
        query = query.filter(Item.name.contains(search_name))

    # ジャンルでフィルター
    if filter_genre:
        query = query.filter(Genre.name == filter_genre)

    # 日付範囲でフィルター
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(StockHistory.created_at >= start_dt)
        except ValueError:
            pass  # 日付が不正な場合は無視

    if end_date:
        try:
            # 終了日の23:59:59までを含める
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(StockHistory.created_at <= end_dt)
        except ValueError:
            pass

    histories = query.all()

    # 全ジャンル取得
    genres = Genre.query.all()

    return render_template(
        'history.html',
        histories=histories,
        genres=genres,
        search_name=search_name,
        filter_genre=filter_genre,
        start_date=start_date,
        end_date=end_date
    )


@app.route('/stock', methods=['GET'])
def stock():
    # フォームの検索パラメータを取得
    search_name = request.args.get('search_name', '')  # アイテム名で検索
    filter_genre = request.args.get('filter_genre', '')  # ジャンルでフィルター

    # Item と Stock と Genre を結合
    query = (
        db.session.query(
            Item,
            Stock.quantity.label('quantity'),
            Genre.name.label('genre_name')
        )
        .join(Stock, Item.id == Stock.item_id)
        .join(Genre, Item.genre_id == Genre.id)
    )

    # アイテム名で部分一致検索
    if search_name:
        query = query.filter(Item.name.contains(search_name))

    # ジャンルでフィルター
    if filter_genre:
        query = query.filter(Genre.name == filter_genre)

    # 結果取得
    items = query.all()

    # 全ジャンルリストを取得（フィルター用）
    genres = Genre.query.all()

    return render_template('stock.html', items=items, genres=genres, search_name=search_name, filter_genre=filter_genre)



# templateフォルダ内のstock.htmlを表示

@app.route('/edit')
def edit() : return render_template('edit.html')
# templateフォルダ内のstock.htmlを表示


if __name__ == '__main__' : 
    app.run(debug=True,port=5002)

