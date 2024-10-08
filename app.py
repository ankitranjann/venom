from flask import Flask, render_template, request, jsonify
import pyodbc

app = Flask(__name__)

# Database connection configuration
server = 'YOUR_SERVER_NAME'
database = 'YOUR_DATABASE_NAME'
username = 'YOUR_USERNAME'
password = 'YOUR_PASSWORD'
driver = '{ODBC Driver 17 for SQL Server}'

# Function to get database connection with error handling
def get_db_connection():
    try:
        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan_barcode', methods=['POST'])
def scan_barcode():
    try:
        barcode = request.json.get('barcode')  # Using .json for security (explained below)
        
        if not barcode:
            return jsonify({'status': 'error', 'message': 'No barcode provided!'}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({'status': 'error', 'message': 'Database connection failed!'}), 500

        cursor = conn.cursor()

        # Check if barcode exists in table1
        cursor.execute("SELECT * FROM table1 WHERE barcode = ?", barcode)
        result = cursor.fetchone()

        if result:
            # Barcode exists, write 0 to table2
            cursor.execute("UPDATE table2 SET value = 0 WHERE barcode = ?", barcode)
            conn.commit()
            return jsonify({'status': 'success', 'message': 'Barcode already exists, updated table2 with 0'})
        else:
            # Barcode does not exist, insert into table1 and write 1 to table2
            cursor.execute("INSERT INTO table1 (barcode) VALUES (?)", barcode)
            cursor.execute("INSERT INTO table2 (barcode, value) VALUES (?, 1)", barcode)
            conn.commit()
            return jsonify({'status': 'success', 'message': 'New barcode added to table1, updated table2 with 1'})

    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return jsonify({'status': 'error', 'message': 'Database error occurred!'}), 500
    except Exception as e:
        print(f"General error: {e}")
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred!'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/view_table1')
def view_table1():
    try:
        conn = get_db_connection()
        if conn is None:
            return render_template('error.html', message="Database connection failed!")

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM table1")
        data = cursor.fetchall()
        return render_template('view_table.html', table='Table 1', data=data)
    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return render_template('error.html', message="Database error occurred!")
    finally:
        if conn:
            conn.close()

@app.route('/view_table2')
def view_table2():
    try:
        conn = get_db_connection()
        if conn is None:
            return render_template('error.html', message="Database connection failed!")

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM table2")
        data = cursor.fetchall()
        return render_template('view_table.html', table='Table 2', data=data)
    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return render_template('error.html', message="Database error occurred!")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
