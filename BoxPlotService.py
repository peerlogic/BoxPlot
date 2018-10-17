import sqlite3, flask, uuid, json
from flask import Flask, render_template, jsonify, request
from flask_api import status

app = Flask(__name__)

def connect_to_db():
    db = None
    curr = None
    try:
        db = sqlite3.connect('config.db', check_same_thread=False)
        cur = db.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS Config (id VARCHAR, json TEXT, temp TINYINT)")
        db.commit()
    except sqlite3.Error as e:
        print("MySQL Error: %s", str(e))
    return db, cur

@app.route('/config', methods=['POST'])
def config():
    db, cur = connect_to_db()
    try:
        id = uuid.uuid4()
        conf = request.json
        query = "INSERT INTO config (id,json,temp) VALUES (?,?,0)"
        cur.execute(query,(str(id),json.dumps(conf)))
        db.commit()

        return jsonify(url = "http://127.0.0.1:5000/" + "chart/" + str(id))
    except Exception as e:
        return jsonify(error = str(e))

@app.route('/temp_config', methods=['POST'])
def temp_config():
    db, cur = connect_to_db()
    try:
        id = uuid.uuid4()
        conf = request.get_json(force=True)
        query = "INSERT INTO config (id,json,temp) VALUES (?,?,1)"
        cur.execute(query,(str(id),json.dumps(conf)))
        db.commit()
        print("http://127.0.0.1:5000/" + "chart/" + str(id))
        return jsonify(url = "http://127.0.0.1:5000/" + "chart/" + str(id))
    except Exception as e:
        return jsonify(error = str(e))

@app.route('/chart/<id>', methods=['GET','DELETE'])
def visualize_chart(id):
    db, cur = connect_to_db()
    if request.method == 'DELETE':
        cur.execute("DELETE FROM config WHERE id = ?",(id,))
        db.commit()
        return "", status.HTTP_200_OK
    else:
        try:
            cur.execute("SELECT json FROM Config WHERE id = ?", (id,))
            rows = cur.fetchall()

            json_data = rows[0][0]
            print(json_data)
            return render_template('visualization.html', json_data = json_data)
        except Exception as e:
            return jsonify(error = str(e))
        # return jsonify(error="Shoot.. I couldn't find the config data")

if __name__ == "__main__":
    connect_to_db()
    app.run(debug=True)
