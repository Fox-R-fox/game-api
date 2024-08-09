from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tictactoe_user:securepassword@postgres-service:5432/tictactoe_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    wins = db.Column(db.Integer, default=0)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 409

    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid username or password"}), 401

    return jsonify({"message": "Login successful"}), 200

@app.route('/update_leaderboard', methods=['POST'])
def update_leaderboard():
    data = request.get_json()
    username = data['username']

    user = User.query.filter_by(username=username).first()
    if user:
        user.wins += 1
        db.session.commit()
        return jsonify({"message": "Leaderboard updated"}), 200
    return jsonify({"message": "User not found"}), 404

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    users = User.query.order_by(User.wins.desc()).all()
    leaderboard = [{"username": user.username, "wins": user.wins} for user in users]
    return jsonify(leaderboard), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
