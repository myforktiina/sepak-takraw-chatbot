from flask import Flask, render_template, request, jsonify, url_for
from chatbot import get_response

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")
    reply = get_response(user_input)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
