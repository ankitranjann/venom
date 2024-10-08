import pyodbc
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Database connection function
def connect_db():
    conn = pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=YOUR_SERVER;"
        "Database=YOUR_DATABASE;"
        "UID=YOUR_USERNAME;"
        "PWD=YOUR_PASSWORD;"
    )
    return conn

# Route to load the UI
@app.route('/')
def index():
    return render_template('index.html')

# API to check barcode in DB
@app.route('/check_barcode', methods=['POST'])
def check_barcode():
    barcode_data = request.json['barcode']

    conn = connect_db()
    cursor = conn.cursor()

    # Query to check if barcode exists
    query = "SELECT * FROM BarcodeTable WHERE barcode = ?"
    cursor.execute(query, (barcode_data,))
    row = cursor.fetchone()

    if row:
        return jsonify({'message': 'The mentioned detail already in Database'})
    else:
        # If not found, insert into database
        insert_query = "INSERT INTO BarcodeTable (barcode) VALUES (?)"
        cursor.execute(insert_query, (barcode_data,))
        conn.commit()
        return jsonify({'message': 'Barcode added successfully'})

if __name__ == '__main__':
    app.run(debug=True)
