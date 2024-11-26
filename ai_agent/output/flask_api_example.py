from flask import Flask, request, jsonify
app = Flask(__name__) # create Flask app

# in-memory database (dictionary) to store items
db = {
}

@app.route('/create', methods=['POST'])
def create_item():
    item = request.get_json() # get JSON data from POST request
    db[item['id']] = item # add item to in-memory database
    return jsonify({'status': 'success'})

@app.route('/read/<string:id>', methods=['GET'])
def read_item(id):
    if id not in db:
        return jsonify({'error': 'Item not found'})
    else:
        return jsonify(db[id])

@app.route('/update/<string:id>', methods=['PUT'])
def update_item(id):
    if id not in db:
        return jsonify({'error': 'Item not found'})
    else:
        new_data = request.get_json() # get updated data from PUT request
        db[id] = new_data  # update item in in-memory database
        return jsonify({'status': 'success'})

@app.route('/delete/<string:id>', methods=['DELETE'])
def delete_item(id):
    if id not in db:
        return jsonify({'error': 'Item not found'})
    else:
        del db[id] # remove item from in-memory database
        return jsonify({'status': 'success'})
if __name__ == '__main__':
    app.run(debug=True)