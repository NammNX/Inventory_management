import os
from datetime import datetime
import app as app
from bson import ObjectId
from flask import Flask, request, render_template, url_for, redirect, flash
import pymongo
import secrets
from werkzeug.utils import secure_filename



app.secret_key = secrets.token_hex(16)



app = Flask(__name__)



app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'myapp/static/uploads')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
collection = db['items']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/list_items')
def list_items():
    items = collection.find()
    return render_template('list_items.html', items=items)


@app.route('/add_items', methods=['GET', 'POST'])
def add_items():
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        current_time = datetime.now()
        filename = None

        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                # Nếu file hình ảnh được tải lên thì lưu vào folder UPLOAD_FOLDER
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        items = {'name': name, 'code': code, 'image': filename, 'timestamp': current_time}
        collection.insert_one(items)

    items = collection.find()
    return render_template('add_items.html', items=items)



@app.route('/search_items', methods=['GET', 'POST'])
def search_items():
    search_query = request.form.get('search_query')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    items_ids = request.form.getlist('items_ids')
    if request.method == 'POST' and items_ids:
        for items_id in items_ids:
            if ObjectId.is_valid(items_id):
                collection.delete_one({"_id": ObjectId(items_id)})
        flash('Selected items have been deleted!', 'success')

    items = []
    query = {}

    if search_query:
        query['$or'] = [
            {'name': {'$regex': search_query, '$options': 'i'}},
            {'code': {'$regex': search_query, '$options': 'i'}}
        ]

    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        query['timestamp'] = {'$gte': start_date, '$lte': end_date}
    elif start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        query['timestamp'] = {'$gte': start_date}
    elif end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        query['timestamp'] = {'$lte': end_date}

    items += collection.find(query)


    return render_template('search.html', items=items)


@app.route('/delete', methods=['GET', 'POST'])
def delete_items():
    items = collection.find()
    if request.method == 'POST':
        items_ids = request.form.getlist('items_ids')
        for items_id in items_ids:
            if ObjectId.is_valid(items_id):
                # if input is a valid ObjectId, delete customer by _id
                collection.delete_one({"_id": ObjectId(items_id)})
        flash('Selected customers have been deleted!', 'success')
        return redirect(url_for('delete_items'))

    return render_template('delete.html', items=items)



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run()
    app.run(debug=True)
