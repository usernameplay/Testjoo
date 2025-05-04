from flask import Flask, request, jsonify
import requests
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad
import base64

app = Flask(__name__)

# Decryption function for encrypted media URL
def decipher(encrypted_media_url: str):
    cipher = DES.new(b'38346591', DES.MODE_ECB)
    decy = unpad(cipher.decrypt(base64.b64decode(encrypted_media_url)), block_size=8)
    return decy.decode()

@app.route('/')
def index():
    return 'home'

@app.route('/api/trending/malayalam')
def getTrendingMalayalam():
    url = "https://www.jiosaavn.com/api.php?__call=content.getTrending&api_version=4&_format=json&_marker=0&ctx=wap6dot0&entity_type=song&entity_language=malayalam"
    res = requests.get(url)
    data = res.json()
    
    songs = data.get("songs", {}).get("data", [])
    trending = []

    for song in songs:
        try:
            trending.append({
                "album": song["album"],
                "play_count": song.get("play_count", ""),
                "has_lyrics": song.get("has_lyrics", ""),
                "artists": song.get("singers", "Various Artists"),
                "year": song.get("year", ""),
                "url": {
                    "320kbps": decipher(song["encrypted_media_url"]).replace("_96", "_320") if song.get("320kbps") == "true" else "",
                },
                "image": {
                    "500X500": song["image"].replace("150x150", "500x500")
                },
                "title": song["title"]
            })
        except Exception as e:
            continue  # Skip any problematic songs

    return jsonify({"results": trending})


@app.route('/api/search/songs')
def searchSongs():
    query = request.args.get('q')
    page = '1' if request.args.get('p') in [None, ""] else request.args.get('p')
    if not query:
        return jsonify({"Error": "Please Provide a Query"})

    res = requests.get(f'https://www.jiosaavn.com/api.php?__call=search.getResults&_format=json&_marker=0&cc=in&includeMetaTags=1&p={page}&q={query}')
    li = []
    for song in res.json()["results"]:
        li.append({
            "album": song["album"],
            "play_count": song["play_count"],
            "has_lyrics": song["has_lyrics"],
            "artists": song["singers"] if song["singers"] != "" else "Various Artists",
            "year": song["year"],
            "url": {
                "320kbps": decipher(song["encrypted_media_url"]).replace("_96", "_320") if song["320kbps"] == "true" else "",
            },
            "image": {
                "500X500": song["image"].replace('150x150', '500x500')
            },
            "title": song["song"]
        })
    return jsonify({"results": li})


@app.route('/api/search/albums')
def searchAlbums():
    query = request.args.get('q')
    page = '1' if request.args.get('p') in [None, ""] else request.args.get('p')
    if not query:
        return "Please enter a valid query"

    res = requests.get(f'https://www.jiosaavn.com/api.php?__call=search.getAlbumResults&_format=json&_marker=0&cc=in&includeMetaTags=1&q={query}&p={page}')
    li = []
    for album in res.json()["results"]:
        li.append({
            "album_id": album["albumid"],
            "artists": album["primary_artists"],
            "thumbnailUrl": {
                "500X500": album["image"].replace('150x150', '500x500'),
            },
            "title": album["title"],
            "year": album["year"]
        })
    return jsonify(li)


@app.route('/api/search/artists')
def searchArtists():
    query = request.args.get('q')
    if not query:
        return "Please enter a valid query"
    res = requests.get(f'https://www.jiosaavn.com/api.php?__call=search.getArtistResults&_format=json&_marker=0&cc=in&includeMetaTags=1&q={query}')
    return res.json()


@app.route('/api/search/playlists')
def searchPlaylist():
    query = request.args.get('q')
    if not query:
        return "Please enter a valid query"
    res = requests.get(f'https://www.jiosaavn.com/api.php?__call=search.getPlaylistResults&_format=json&_marker=0&cc=in&includeMetaTags=1&q={query}')
    return res.json()


if __name__ == '__main__':
    app.run(debug=True)
