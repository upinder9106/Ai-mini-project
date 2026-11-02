"""
Test suite for revamped MOODIFY AI (Museverse UI + 7 Artists, 49 Songs)
"""

import unittest
import json
from app import app
from mood_engine import MoodEngine


class TestMoodifyAI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.client = app.test_client()
        cls.engine = MoodEngine()

    def test_homepage(self):
        """Test index route loads HTML and brand"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MOODIFY', response.data)
        # Verify YBE SINGH is completely removed
        self.assertNotIn(b'YBE SINGH', response.data)

    def test_get_songs(self):
        """Test songs API endpoint returns 49 songs"""
        response = self.client.get('/api/songs')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 49)

    def test_no_ybe_singh(self):
        """Verify YBE SINGH is not present in songs or artists"""
        response = self.client.get('/api/songs')
        data = json.loads(response.data)
        for s in data['songs']:
            self.assertNotEqual(s.get('artist_id'), 'ybe-singh')
            self.assertNotEqual(s.get('artist'), 'YBE SINGH')

        art_res = self.client.get('/api/artists')
        art_data = json.loads(art_res.data)
        for a in art_data['artists']:
            self.assertNotEqual(a.get('id'), 'ybe-singh')
            self.assertNotEqual(a.get('name'), 'YBE SINGH')

    def test_seven_artists_presence(self):
        """Verify the 7 requested artists are all present with 7 songs each"""
        expected_artists = [
            'shubh', 'diljit-dosanjh', 'sidhu-moosewala', 'karan-aujla',
            'the-weeknd', 'travis-scott', 'taylor-swift'
        ]
        response = self.client.get('/api/artists')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['count'], 7)

        artist_ids = [a['id'] for a in data['artists']]
        for ea in expected_artists:
            self.assertIn(ea, artist_ids)

        # Check each artist has 7 tracks
        songs_res = self.client.get('/api/songs')
        songs_data = json.loads(songs_res.data)
        for ea in expected_artists:
            count = sum(1 for s in songs_data['songs'] if s['artist_id'] == ea)
            self.assertEqual(count, 7, f"Artist {ea} should have 7 songs, got {count}")

    def test_all_six_moods_endpoints(self):
        """Test each of the 6 moods has curated songs"""
        for mood in ["Happy", "Sad", "Angry", "Romantic", "Energetic", "Chill"]:
            response = self.client.get(f'/api/mood/{mood}')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertGreater(data['count'], 0)

    def test_text_mood_detection(self):
        """Test text detection algorithm for all 6 mood classes"""
        test_cases = [
            ("Bhangra party nachna full celebration dancing", "Happy"),
            ("Dil tuteya broken heart lonely tears all too well", "Sad"),
            ("Badla revenge 295 drill fein moshpit rage angry", "Angry"),
            ("Pyar ishq soniye romantic lover die for you date", "Romantic"),
            ("Gym workout beast mode sicko mode blinding lights speed", "Energetic"),
            ("Sukoon quiet rain coffee cardigan highest in the room chill", "Chill")
        ]

        for prompt, expected_mood in test_cases:
            response = self.client.post('/api/mood/detect',
                                        data=json.dumps({"text": prompt}),
                                        content_type='application/json')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            detected = data['detection']['primary_mood']
            self.assertEqual(detected, expected_mood)
            self.assertGreater(len(data['recommendations']), 0)

    def test_spotify_and_youtube_links(self):
        """Verify songs have valid Spotify and YouTube redirect links"""
        response = self.client.get('/api/songs')
        data = json.loads(response.data)
        for s in data['songs']:
            self.assertTrue(s.get('spotify_url', '').startswith('https://open.spotify.com/'))
            self.assertTrue(s.get('youtube_url', '').startswith('https://www.youtube.com/'))

    def test_preset_playlists(self):
        """Verify preset playlists include September Vibes and Chill Story with approved artists only"""
        response = self.client.get('/api/playlists/presets')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        pls = data['playlists']
        self.assertIn('pl-september', pls)
        self.assertIn('pl-chill', pls)
        self.assertEqual(pls['pl-september']['name'], 'September Vibes')
        self.assertEqual(pls['pl-chill']['name'], 'Chill Story')

        # Check all songs in presets belong to approved 7 artists
        songs_res = self.client.get('/api/songs')
        songs_data = json.loads(songs_res.data)
        valid_song_ids = set(s['id'] for s in songs_data['songs'])

        for pl_key, pl_val in pls.items():
            for sid in pl_val['song_ids']:
                self.assertIn(sid, valid_song_ids, f"Song {sid} in preset {pl_key} not in approved database")

    def test_auth_login_and_register(self):
        """Test login and registration endpoints"""
        # Test demo user login
        login_res = self.client.post('/api/auth/login',
                                     data=json.dumps({"username": "user", "password": "pass123"}),
                                     content_type='application/json')
        self.assertEqual(login_res.status_code, 200)
        login_data = json.loads(login_res.data)
        self.assertTrue(login_data['success'])
        self.assertEqual(login_data['user']['username'], 'user')

        # Test registration
        reg_res = self.client.post('/api/auth/register',
                                   data=json.dumps({"username": "newtestuser", "password": "mypassword", "name": "Test User"}),
                                   content_type='application/json')
        self.assertEqual(reg_res.status_code, 200)
        reg_data = json.loads(reg_res.data)
        self.assertTrue(reg_data['success'])
        self.assertEqual(reg_data['user']['username'], 'newtestuser')


if __name__ == '__main__':
    unittest.main()
