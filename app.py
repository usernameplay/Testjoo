from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

JIOSAAVN_URL = "https://www.jiosaavn.com/api.php?__call=content.getTrending&api_version=4&_format=json&_marker=0&ctx=wap6dot0&entity_type=album&entity_language=malayalam"

@app.route("/")
def home():
    res = requests.get(JIOSAAVN_URL, headers={"User-Agent": "Mozilla/5.0"})
    data = res.json()
    albums = data.get("trending", {}).get("albums", {}).get("items", [])
    return render_template("index.html", albums=albums)

if __name__ == "__main__":
    app.run(debug=True)
