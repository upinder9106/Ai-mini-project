# 🎧 MOODIFY AI – Modern Mood Music Streaming & Mood Sets

MOODIFY AI is a music streaming web application designed with a sleek, dark aesthetic (inspired by Museverse / Spotify / Tidal). It features an interactive **Mood Set Selector**, an **AI Mood Detector**, and an iconic 49-song roster across 7 global and Punjabi superstars.

---

## 🌟 Featured Artists (7 Tracks Each with Diverse Mood Sets)

1. **Shubh** (*Cheques, No Love, Baller, Elevated, Her, One Love, King Shit*)
2. **Diljit Dosanjh** (*Lover, Born to Shine, G.O.A.T., Naina, Hass Hass, Peaches, Lemonade*)
3. **Sidhu Moosewala** (*295, The Last Ride, So High, Levels, Dear Mama, Old Skool, Same Beef*)
4. **Karan Aujla** (*Softly, Tauba Tauba, Winning Speech, 52 Bars, Admirin' You, Chitta Kurta, Antidote*)
5. **The Weeknd** (*Blinding Lights, Save Your Tears, Starboy, Die For You, The Hills, Out of Time, Call Out My Name*)
6. **Travis Scott** (*SICKO MODE, FE!N, Goosebumps, HIGHEST IN THE ROOM, MY EYES, TELEKINESIS, BUTTERFLY EFFECT*)
7. **Taylor Swift** (*Cruel Summer, Anti-Hero, Blank Space, Lover, All Too Well 10min, Bad Blood, Cardigan*)

---

## 🎨 UI & Features (Museverse Design System)

- **Sidebar Navigation & Playlists**:
  - `Explore`, `Chart`, `History`
  - `MY LIBRARY`: Mixes and Radio, Playlists, Albums, Tracks, Artists
  - `MY PLAYLISTS`: Curated collections (`September Vibes`, `Chill Story`, `Mixes and Radio`, `Clubbing & Drill`, `❤️ Liked Songs`) + custom user playlists + `+ New Playlist` creator.
  - Dedicated **Playlist View Banner** with `▶ Play Entire Playlist`, `➕ Add Songs to Playlist`, `🗑️ Delete Playlist`, and instant `✕ Remove` buttons on songs.
- **Top Navigation Bar & Authentication**:
  - History arrows (`< >`), Pill Search box (`🔍 Search`), AI Mood Detector trigger (`✨ AI Mood Detector`).
  - **🔔 Notification Panel & Mood History**: View chronological history of selected/detected moods with 1-click **Reactivate** buttons, plus activity logs.
  - **👤 User Login & Registration**: Modern modal supporting User ID & Password login, account registration, and personalized playlists/favourites.
- **Mood Set Selector (1-Click Filtering)**:
  - `✨ All Moods`, `🎉 Happy`, `💔 Sad`, `🔥 Angry`, `🌹 Romantic`, `⚡ Energetic`, `🌙 Chill`.
  - Instantly filters songs into mood sets across all 7 approved artists upon clicking.
- **Featured & New Arrivals**:
  - Rectangular cards with category badges (`NEW FOR YOU`, `NEW ALBUM`, `TRENDING`), bold typography, and a **floating white circular play button (`▶`)**.
- **Artists Row**:
  - Circular artist avatars with glowing ring frames for all 7 artists. Clicking any artist instantly filters their discography.
- **Add to Playlist Everywhere**:
  - Every music card and table row features an interactive **`➕ Add to Playlist`** button and a **`❤️ Favourite`** button.
- **One-Click Official Redirects**:
  - Direct **🟢 Spotify** and **🔴 YouTube** buttons on every single music card, table row, and inside the fixed player bar.
- **Fixed Bottom Music Player**:
  - Square album cover, track title, heart `♡` button, artist, `PLAYING FROM: ...`.
  - Full playback controls: Shuffle, Previous, Big White Play/Pause Circle, Next, Repeat.
  - Interactive scrubbable progress bar with real-time timestamps.
  - Volume slider and mute toggle.

---

## 🚀 How to Run the Application

```bash
cd "C:\Users\Upinder\.gemini\antigravity\scratch\MOODIFY_AI"
pip install -r requirements.txt
python app.py
```

Open your browser at:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**
