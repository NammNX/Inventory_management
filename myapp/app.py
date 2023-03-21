import app as app
from bson import ObjectId
from flask import Flask, request, render_template, url_for, redirect, flash
import pymongo
import secrets

app.secret_key = secrets.token_hex(16)



app = Flask(__name__)

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
        items = {'name': name, 'code': code}
        collection.insert_one(items)

    items = collection.find()
    return render_template('add_items.html', items=items)

@app.route('/search_items', methods=['GET', 'POST'])
def search_items():
    name = request.form.get('name')
    code = request.form.get('code')
    items = []
    if name and code:
        items += collection.find({'name': name, 'code': code})
    elif name:
        items += collection.find({'name': name})
    elif code:
        items += collection.find({'code': code})
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
