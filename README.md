# ytmusicapi: Unofficial API for YouTube Music

ytmusicapi is a Python 3 library to send requests to the YouTube Music API.
It emulates YouTube Music web client requests using the user's cookie data for authentication.

---

## Features

- **Browsing**: Search (with all filters) & suggestions, artist details, user info, albums, song metadata, watch playlists, song lyrics.
- **Exploring**: Moods & genres playlists, charts (global and per country).
- **Library management**: Playlists, songs, artists, albums, subscriptions, podcasts, channels, rating songs, and play history.
- **Playlists**: Create, delete, edit metadata, add/move/remove tracks, playlist contents.
- **Podcasts**: Podcasts, episodes, channels, and episode playlists.
- **Uploads**: Upload songs, remove uploads, list uploaded songs/albums/artists.
- **Localization**: Supports all regions and 16 languages.

---

## Requirements

- Python 3.10 or higher - https://www.python.org
- Node.js & Wrangler CLI (for Cloudflare Workers deployment)

---

## Installation & Basic Usage

```bash
pip install ytmusicapi
```

```python
from ytmusicapi import YTMusic

yt = YTMusic('oauth.json')
playlistId = yt.create_playlist('test', 'test description')
search_results = yt.search('Oasis Wonderwall')
yt.add_playlist_items(playlistId, [search_results[0]['videoId']])
```

---

## ⚡ Deploying on Cloudflare Workers

You can easily deploy `ytmusicapi` as a high-performance REST API microservice on **Cloudflare Workers**.

### 1. Prerequisites
- Install [Node.js](https://nodejs.org/) (v18+)
- Install Wrangler CLI:
  ```bash
  npm install -g wrangler
  ```

### 2. Deployment

Log in to Cloudflare and deploy:

```bash
npx wrangler login
npx wrangler deploy
```

Wrangler will build and deploy the worker, giving you a live API endpoint (e.g. `https://ytmusicapi-worker.<your-subdomain>.workers.dev`).

### 3. Local Development

To run and test the Cloudflare worker locally:

```bash
npx wrangler dev
```

The API will be accessible locally at `http://localhost:8787`.

---

## 🌐 Cloudflare API Endpoints & Usage

| Endpoint | Method | Parameters | Description |
|---|---|---|---|
| `/` | `GET` | - | Returns API status & documentation |
| `/search` | `GET` | `q` (required), `filter`, `limit` | Search YouTube Music |
| `/search/suggestions` | `GET` | `q` (required), `detailed` | Get search auto-complete suggestions |
| `/artist` | `GET` | `id` (required) | Get artist details and releases |
| `/album` | `GET` | `id` (required) | Get album details and track list |
| `/playlist` | `GET` | `id` (required), `limit` | Get playlist details and tracks |
| `/song` | `GET` | `id` (required) | Get song metadata |
| `/lyrics` | `GET` | `id` (required) | Get song lyrics |
| `/charts` | `GET` | `country` (optional, default: US) | Get music charts |
| `/watch` | `GET` | `id` (required) | Get watch playlist / radio next tracks |

### Quick Examples

- **Search Songs:**
  ```bash
  curl "https://ytmusicapi-worker.<your-subdomain>.workers.dev/search?q=Radiohead&filter=songs"
  ```

- **Get Album Info:**
  ```bash
  curl "https://ytmusicapi-worker.<your-subdomain>.workers.dev/album?id=MPREb_953CFFR0aYf"
  ```

- **Get Lyrics:**
  ```bash
  curl "https://ytmusicapi-worker.<your-subdomain>.workers.dev/lyrics?id=fJ9rUzIMcZQ"
  ```

---

## Contributing

Pull requests are welcome! Please refer to [CONTRIBUTING.rst](CONTRIBUTING.rst) for guidelines.
