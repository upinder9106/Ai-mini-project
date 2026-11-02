"""
MOODIFY AI - Flask Application Server
AI-Powered Punjabi Music Mood Detector & Recommendation System
"""

import os
import sys
import json

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from flask import Flask, render_template, jsonify, request, send_from_directory
from mood_engine import MoodEngine

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_FILE = os.path.join(BASE_DIR, "songs.json")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["JSON_SORT_KEYS"] = False

# Initialize mood engine
mood_engine = MoodEngine()


def load_database():
    """Load songs and artists from songs.json with fallback handling."""
    try:
        with open(SONGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Handle both {"songs": [...], "artists": [...]} and [...] format
            if isinstance(data, dict):
                songs = data.get("songs", [])
                artists = data.get("artists", [])
            else:
                songs = data
                artists = []
                
            return songs, artists
    except Exception as e:
        print(f"Error loading {SONGS_FILE}: {e}")
        return [], []


@app.route("/")
def index():
    """Render the main single-page music streaming application."""
    return render_template("index.html")


@app.route("/api/songs", methods=["GET"])
def get_songs():
    """
    Fetch songs catalog with optional filtering.
    Query params:
      - mood: Filter by mood name (e.g., 'Energetic', 'Romantic')
      - artist: Filter by artist_id or artist name
      - search: Full-text search term
      - limit: Max number of records to return
    """
    try:
        songs, _ = load_database()
        mood = request.args.get("mood")
        artist = request.args.get("artist")
        search = request.args.get("search")
        limit = request.args.get("limit", type=int)

        filtered = mood_engine.filter_songs(songs, mood=mood, artist_id=artist, search=search)

        if limit and limit > 0:
            filtered = filtered[:limit]

        return jsonify({
            "success": True,
            "count": len(filtered),
            "songs": filtered
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/song/<song_id>", methods=["GET"])
def get_song(song_id):
    """Retrieve details for a specific song ID."""
    try:
        songs, _ = load_database()
        song = next((s for s in songs if s.get("id") == song_id), None)
        if not song:
            return jsonify({"success": False, "error": f"Song with id '{song_id}' not found"}), 404
        return jsonify({"success": True, "song": song})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/moods", methods=["GET"])
def get_moods():
    """Return all 6 supported moods with metadata."""
    return jsonify({
        "success": True,
        "moods": mood_engine.MOODS,
        "metadata": mood_engine.MOOD_METADATA
    })


@app.route("/api/mood/<mood_name>", methods=["GET"])
def get_mood_playlist(mood_name):
    """Get metadata and curated song recommendations for a specific mood."""
    try:
        normalized_mood = mood_name.strip().capitalize()
        if normalized_mood not in mood_engine.MOODS:
            return jsonify({
                "success": False,
                "error": f"Invalid mood '{mood_name}'. Must be one of: {', '.join(mood_engine.MOODS)}"
            }), 400

        songs, _ = load_database()
        curated_songs = mood_engine.filter_songs(songs, mood=normalized_mood)
        meta = mood_engine.MOOD_METADATA.get(normalized_mood, {})

        return jsonify({
            "success": True,
            "mood": normalized_mood,
            "metadata": meta,
            "count": len(curated_songs),
            "songs": curated_songs
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/mood/detect", methods=["POST"])
def detect_mood():
    """
    Analyze user text input to detect mood, generate scores, and return recommendations.
    Request body: { "text": "I feel like driving fast with heavy bass on gedi route" }
    """
    try:
        data = request.get_json(silent=True) or {}
        text = data.get("text", "")
        if not text:
            return jsonify({"success": False, "error": "Missing 'text' field in request payload"}), 400

        # Run AI detection engine
        result = mood_engine.detect_mood(text)
        if not result.get("success"):
            return jsonify(result), 400

        primary_mood = result.get("primary_mood")
        songs, _ = load_database()

        # Prioritize songs matching primary mood; fall back to secondary mood
        matched_songs = mood_engine.filter_songs(songs, mood=primary_mood)
        if len(matched_songs) < 7 and result.get("secondary_mood"):
            secondary_songs = mood_engine.filter_songs(songs, mood=result.get("secondary_mood"))
            for s in secondary_songs:
                if s not in matched_songs:
                    matched_songs.append(s)

        # Diversify recommendations across all available artists
        diversified_recommendations = []
        seen_artists = set()
        for s in matched_songs:
            art = s.get("artist")
            if art not in seen_artists:
                diversified_recommendations.append(s)
                seen_artists.add(art)
        for s in matched_songs:
            if s not in diversified_recommendations:
                diversified_recommendations.append(s)

        return jsonify({
            "success": True,
            "detection": result,
            "recommendations": diversified_recommendations[:14]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/artists", methods=["GET"])
def get_artists():
    """List all artists with bios, socials, and track counts."""
    try:
        songs, artists = load_database()

        # Calculate track count for each artist
        enriched_artists = []
        for art in artists:
            art_id = art.get("id")
            art_songs = [s for s in songs if s.get("artist_id") == art_id or art.get("name", "").lower() in s.get("artist", "").lower()]
            art_copy = dict(art)
            art_copy["track_count"] = len(art_songs)
            enriched_artists.append(art_copy)

        return jsonify({
            "success": True,
            "count": len(enriched_artists),
            "artists": enriched_artists
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/artist/<artist_id>", methods=["GET"])
def get_artist(artist_id):
    """Get single artist information and all their tracks."""
    try:
        songs, artists = load_database()
        art = next((a for a in artists if a.get("id") == artist_id or a.get("name", "").lower() == artist_id.lower()), None)
        
        if not art:
            return jsonify({"success": False, "error": f"Artist '{artist_id}' not found"}), 404

        artist_songs = [
            s for s in songs
            if s.get("artist_id") == art.get("id") or art.get("name", "").lower() in s.get("artist", "").lower()
        ]

        return jsonify({
            "success": True,
            "artist": art,
            "track_count": len(artist_songs),
            "songs": artist_songs
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/search", methods=["GET"])
def search():
    """Unified search endpoint for songs and artists."""
    try:
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"success": True, "songs": [], "artists": []})

        songs, artists = load_database()

        matched_songs = mood_engine.filter_songs(songs, search=query)
        matched_artists = [
            a for a in artists
            if query.lower() in a.get("name", "").lower() or query.lower() in a.get("bio", "").lower()
        ]

        return jsonify({
            "success": True,
            "query": query,
            "songs": matched_songs,
            "artists": matched_artists
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Return platform statistics."""
    try:
        songs, artists = load_database()
        local_audio_count = sum(1 for s in songs if s.get("is_local_audio"))
        mood_counts = {m: sum(1 for s in songs if s.get("mood") == m) for m in mood_engine.MOODS}

        return jsonify({
            "success": True,
            "total_songs": len(songs),
            "total_artists": len(artists),
            "local_playable_tracks": local_audio_count,
            "moods_supported": len(mood_engine.MOODS),
            "mood_distribution": mood_counts
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# In-memory demo users storage (persistent during server life, fallback supported)
USERS_DB = {
    "user": {"username": "user", "password": "pass123", "name": "Demo User"},
    "upinder": {"username": "upinder", "password": "moodify123", "name": "Upinder"}
}

# Curated Presets containing ONLY tracks from the 7 approved artists
PRESET_PLAYLISTS = {
    "pl-september": {
        "id": "pl-september",
        "name": "September Vibes",
        "description": "Autumn vibes and chartbusters from our 7 approved artists",
        "is_preset": True,
        "song_ids": [
            "shubh-cheques",
            "diljit-lover",
            "aujla-softly",
            "weeknd-starboy",
            "taylor-cruel-summer",
            "travis-highest-in-the-room",
            "moosewala-so-high"
        ]
    },
    "pl-chill": {
        "id": "pl-chill",
        "name": "Chill Story",
        "description": "Tranquil midnight melodies and acoustic calm",
        "is_preset": True,
        "song_ids": [
            "diljit-ikk-kudi",
            "taylor-cardigan",
            "moosewala-sohne-lagde",
            "weeknd-save-your-tears",
            "travis-my-eyes",
            "shubh-her",
            "aujla-admirin-you"
        ]
    },
    "pl-mixes": {
        "id": "pl-mixes",
        "name": "Mixes and Radio",
        "description": "Continuous mix of iconic anthems across all 7 artists",
        "is_preset": True,
        "song_ids": [
            "weeknd-blinding-lights",
            "diljit-born-to-shine",
            "shubh-baller",
            "aujla-52-bars",
            "travis-sicko-mode",
            "taylor-blank-space",
            "moosewala-the-last-ride"
        ]
    },
    "pl-clubbing": {
        "id": "pl-clubbing",
        "name": "Clubbing & Drill",
        "description": "High-octane stadium energy and Punjabi trap beats",
        "is_preset": True,
        "song_ids": [
            "moosewala-295",
            "travis-fein",
            "aujla-winning-speech",
            "shubh-king-shit",
            "diljit-goat",
            "weeknd-the-hills",
            "taylor-bad-blood"
        ]
    }
}


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    """User login endpoint with ID and password."""
    try:
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip().lower()
        password = data.get("password", "")

        if not username or not password:
            return jsonify({"success": False, "error": "Username/ID and password are required"}), 400

        # Check existing user
        if username in USERS_DB:
            if USERS_DB[username]["password"] == password:
                u = USERS_DB[username]
                return jsonify({
                    "success": True,
                    "message": "Login successful",
                    "user": {"username": u["username"], "name": u["name"]}
                })
            else:
                return jsonify({"success": False, "error": "Invalid password"}), 401
        else:
            # Auto-provision new user ID so any user can log in seamlessly
            new_user = {"username": username, "password": password, "name": username.capitalize()}
            USERS_DB[username] = new_user
            return jsonify({
                "success": True,
                "message": "New account created and logged in",
                "user": {"username": new_user["username"], "name": new_user["name"]}
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    """User registration endpoint."""
    try:
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip().lower()
        password = data.get("password", "")
        name = (data.get("name") or "").strip() or username.capitalize()

        if not username or not password:
            return jsonify({"success": False, "error": "Username/ID and password are required"}), 400

        if username in USERS_DB:
            return jsonify({"success": False, "error": "Username already exists. Please login."}), 409

        USERS_DB[username] = {"username": username, "password": password, "name": name}
        return jsonify({
            "success": True,
            "message": "Registration successful",
            "user": {"username": username, "name": name}
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/playlists/presets", methods=["GET"])
def get_preset_playlists():
    """Return verified curated presets for September Vibes, Chill Story, Mixes, Clubbing."""
    return jsonify({
        "success": True,
        "playlists": PRESET_PLAYLISTS
    })


# Error Handlers
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404
    return render_template("index.html"), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[MOODIFY AI] Server running on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
