from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data', methods=['GET'])
def get_data():
    # Example data to send to the frontend
    data = {'name': 'John Doe', 'age': 30}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
