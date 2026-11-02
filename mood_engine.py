"""
MOODIFY AI - Mood Detection & Recommendation Engine
Keyword & Scoring Algorithm for Global & Punjabi Music
Supports: Shubh, Diljit Dosanjh, Sidhu Moosewala, Karan Aujla,
The Weeknd, Travis Scott, Taylor Swift.
"""

import re
from typing import Dict, List, Any


class MoodEngine:
    MOODS = ["Happy", "Sad", "Angry", "Romantic", "Energetic", "Chill"]

    MOOD_METADATA = {
        "Happy": {
            "emoji": "🎉",
            "tagline": "Joy, Celebration & Euphoria",
            "color": "#f59e0b",
            "description": "Upbeat party tracks, feel-good pop melodies, and joyful dancefloor anthems."
        },
        "Sad": {
            "emoji": "💔",
            "tagline": "Heartbreak, Tears & Melancholy",
            "color": "#3b82f6",
            "description": "Deeply emotional ballads, heartfelt acoustic confessions, and late-night longing."
        },
        "Angry": {
            "emoji": "🔥",
            "tagline": "Rage, Drill, Vair & Defiance",
            "color": "#ef4444",
            "description": "Heavy 808s, street rivalry anthems, savage punchlines, and moshpit trap."
        },
        "Romantic": {
            "emoji": "🌹",
            "tagline": "Love, Passion & Intimacy",
            "color": "#ec4899",
            "description": "Sweet acoustic melodies, timeless love waltzes, and starry midnight serenades."
        },
        "Energetic": {
            "emoji": "⚡",
            "tagline": "Hype, Stadium Anthems & Workout",
            "color": "#8b5cf6",
            "description": "Stadium-shaking beats, high-speed night drives, synthwave pulses, and gym fuel."
        },
        "Chill": {
            "emoji": "🌙",
            "tagline": "Sukoon, Indie Synths & Lofi",
            "color": "#06b6d4",
            "description": "Mellow indie guitars, relaxed coffeehouse vibes, peaceful rain, and serene unwinding."
        }
    }

    LEXICON = {
        "Happy": {
            "keywords": [
                "happy", "joy", "cheerful", "party", "dance", "celebrate", "celebration", "bhangra",
                "nachna", "khushi", "hasna", "smile", "laugh", "fun", "masti", "mauja", "excited",
                "upbeat", "good vibes", "sunny", "sunshine", "dancing", "cruel summer", "born to shine",
                "shadi", "wedding", "festive", "enjoy", "feel good", "butterfly", "pop"
            ],
            "weight": 1.2
        },
        "Sad": {
            "keywords": [
                "sad", "unhappy", "depressed", "sorrow", "grief", "broken", "heartbreak", "heartbroken",
                "alone", "lonely", "tears", "cry", "crying", "pain", "hurt", "miss", "missing", "melancholy",
                "dil tuteya", "dard", "hanju", "rove", "rona", "judai", "bewafa", "yaadan", "tanha",
                "broke up", "breakup", "lost", "all too well", "save your tears", "empty", "cry myself to sleep"
            ],
            "weight": 1.3
        },
        "Angry": {
            "keywords": [
                "angry", "mad", "furious", "rage", "revenge", "badla", "vair", "dushmani", "fight",
                "fighting", "hater", "haters", "beef", "rival", "rivalry", "destroy", "aggressive",
                "bad blood", "fein", "moshpit", "fe!n", "kill", "danger", "violent", "wrath", "drill",
                "295", "baller", "52 bars", "savage", "furious", "hate", "pissed"
            ],
            "weight": 1.3
        },
        "Romantic": {
            "keywords": [
                "romantic", "love", "loving", "romance", "crush", "beloved", "sweetheart", "darling",
                "pyar", "ishq", "mohabbat", "soniye", "lover", "die for you", "softly", "naina",
                "date", "kiss", "kisses", "hugs", "cuddle", "beautiful", "sohni", "chand", "tare",
                "falling in love", "true love", "sweetheart", "heartbeat", "forever and always"
            ],
            "weight": 1.2
        },
        "Energetic": {
            "keywords": [
                "energetic", "energy", "hype", "pumped", "gym", "workout", "lifting", "heavy", "beast",
                "beast mode", "gedi", "speed", "drift", "bass", "subwoofer", "blinding lights", "sicko mode",
                "starboy", "cheques", "so high", "stadium", "adrenaline", "fire", "explosive", "boost",
                "running", "unstoppable", "heavy bass", "hardcore", "drop"
            ],
            "weight": 1.3
        },
        "Chill": {
            "keywords": [
                "chill", "relax", "relaxing", "calm", "peace", "peaceful", "quiet", "serene", "sukoon",
                "shanti", "coffee", "tea", "chai", "balcony", "rain", "breeze", "soft", "lofi", "ambient",
                "cardigan", "highest in the room", "anti hero", "late night", "midnight", "slow",
                "unwind", "cozy", "comfort", "soothing", "peace of mind", "mellow"
            ],
            "weight": 1.2
        }
    }

    NEGATIONS = ["not", "never", "no", "nahi", "ni", "don't", "dont", "hardly", "barely"]
    INTENSIFIERS = ["very", "super", "extremely", "bohot", "bahut", "too", "so", "ultra", "way too"]

    def __init__(self):
        self._compiled_lexicon = {}
        for mood, data in self.LEXICON.items():
            self._compiled_lexicon[mood] = []
            for phrase in data["keywords"]:
                pattern = r'\b' + re.escape(phrase.lower()) + r'\b'
                self._compiled_lexicon[mood].append((phrase, re.compile(pattern, re.IGNORECASE)))

    def detect_mood(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {"success": False, "error": "Please enter how you are feeling or describe your scene."}

        cleaned = text.strip()
        lower = cleaned.lower()

        scores = {m: 0.0 for m in self.MOODS}
        matched_details = {m: [] for m in self.MOODS}

        has_intensifier = any(inte in lower for inte in self.INTENSIFIERS)
        multiplier = 1.4 if has_intensifier else 1.0

        for mood, phrases in self._compiled_lexicon.items():
            base_weight = self.LEXICON[mood]["weight"]
            for phrase, regex in phrases:
                matches = regex.findall(lower)
                if matches:
                    count = len(matches)
                    is_neg = any(re.search(rf'\b{re.escape(n)}\s+(?:\w+\s+)?{re.escape(phrase)}', lower) for n in self.NEGATIONS)
                    if is_neg:
                        scores[mood] = max(0.0, scores[mood] - 1.5)
                    else:
                        scores[mood] += count * base_weight * multiplier
                        if phrase not in matched_details[mood]:
                            matched_details[mood].append(phrase)

        total_score = sum(scores.values())
        if total_score == 0.0:
            return self._fallback_detection(cleaned)

        confidence_distribution = {m: round((scores[m] / total_score) * 100, 1) for m in self.MOODS}
        sorted_moods = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_mood, top_score = sorted_moods[0]
        secondary_mood, second_score = sorted_moods[1]

        primary_conf = min(98.0, max(65.0, confidence_distribution[primary_mood]))

        matched_kws = matched_details[primary_mood]
        if secondary_mood and matched_details[secondary_mood]:
            matched_kws = matched_kws + [f"{k} ({secondary_mood.lower()})" for k in matched_details[secondary_mood][:2]]

        explanation = self._generate_explanation(primary_mood, secondary_mood if second_score > 0 else None, primary_conf, matched_details[primary_mood])

        return {
            "success": True,
            "query": cleaned,
            "primary_mood": primary_mood,
            "secondary_mood": secondary_mood if second_score > 0 else "Chill",
            "confidence": primary_conf,
            "confidence_distribution": confidence_distribution,
            "matched_keywords": matched_kws[:6],
            "explanation": explanation,
            "metadata": self.MOOD_METADATA.get(primary_mood, {})
        }

    def _fallback_detection(self, text: str) -> Dict[str, Any]:
        mood = "Energetic" if "!" in text else "Chill"
        conf = 68.0
        dist = {m: 6.4 for m in self.MOODS}
        dist[mood] = conf
        return {
            "success": True,
            "query": text,
            "primary_mood": mood,
            "secondary_mood": "Happy",
            "confidence": conf,
            "confidence_distribution": dist,
            "matched_keywords": ["ambient vibe", "natural tone"],
            "explanation": f"MOODIFY AI detected an engaging {mood} atmosphere tailored to your prompt.",
            "metadata": self.MOOD_METADATA.get(mood, {})
        }

    def _generate_explanation(self, primary_mood: str, secondary_mood: str, confidence: float, keywords: List[str]) -> str:
        kw_str = f"'{', '.join(keywords[:3])}'" if keywords else "lyrical indicators"
        explanations = {
            "Happy": f"Detected vibrant celebration and optimistic euphoria ({confidence}% confidence) with cues {kw_str}.",
            "Sad": f"Identified deep emotional longing and heartbreak nuances ({confidence}% confidence) via {kw_str}.",
            "Angry": f"Detected heavy street defiance, rage, and adrenaline ({confidence}% confidence) based on {kw_str}.",
            "Romantic": f"Warm affection and intimate passion detected ({confidence}% confidence) with {kw_str}.",
            "Energetic": f"High arousal workout, stadium anthems, and speed cues detected ({confidence}% confidence) via {kw_str}.",
            "Chill": f"Gentle, tranquil and relaxing atmosphere detected ({confidence}% confidence) with {kw_str}."
        }
        res = explanations.get(primary_mood, f"Detected {primary_mood} mood.")
        if secondary_mood and secondary_mood != primary_mood:
            res += f" With secondary notes of {secondary_mood}."
        return res

    def filter_songs(self, songs: List[Dict[str, Any]], mood: str = None, artist_id: str = None, search: str = None) -> List[Dict[str, Any]]:
        results = songs
        if mood and mood.lower() != 'all':
            m = mood.strip().lower()
            results = [s for s in results if s.get("mood", "").lower() == m or s.get("secondary_mood", "").lower() == m]
        if artist_id and artist_id.lower() != 'all':
            a = artist_id.strip().lower()
            results = [s for s in results if s.get("artist_id", "").lower() == a or a in s.get("artist", "").lower()]
        if search:
            q = search.strip().lower()
            results = [
                s for s in results
                if q in s.get("title", "").lower()
                or q in s.get("artist", "").lower()
                or q in s.get("album", "").lower()
                or any(q in t.lower() for t in s.get("tags", []))
            ]
        return results
