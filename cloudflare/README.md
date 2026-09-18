# Deploying ytmusicapi to Cloudflare Workers

Easily deploy `ytmusicapi` as a high-performance REST API on **Cloudflare Workers** using Cloudflare's native Python Workers runtime.

---

## Prerequisites

Before starting, ensure you have:
1. **Node.js** (v18+) installed.
2. A **Cloudflare account** (Free or Paid).
3. **Wrangler CLI** installed globally or via `npx`:
   ```bash
   npm install -g wrangler
   ```

---

## Quick Start Deployment

1. **Clone the repository & navigate to the `cloudflare` directory:**
   ```bash
   cd cloudflare
   ```

2. **Login to Cloudflare:**
   ```bash
   npx wrangler login
   ```

3. **Deploy the Worker:**
   ```bash
   npx wrangler deploy
   ```

Upon deployment, Wrangler will output your Worker's live URL (e.g., `https://ytmusicapi-worker.<your-subdomain>.workers.dev`).

---

## Testing Locally

You can test and run the Worker on your local machine using Wrangler:

```bash
npx wrangler dev
```

Your API will be running locally at `http://localhost:8787`.

---

## API Endpoints & Usage Examples

### 1. Root / Status
- **Endpoint:** `GET /`
- **Example:**
  ```bash
  curl https://ytmusicapi-worker.<your-subdomain>.workers.dev/
  ```

### 2. Search
- **Endpoint:** `GET /search?q=<query>&filter=<type>&limit=<number>`
- **Parameters:**
  - `q` (required): Search query (e.g., `Ishq` or `Oasis Wonderwall`)
  - `filter` (optional): `songs`, `videos`, `albums`, `artists`, `playlists`, `community_playlists`, `featured_playlists`
  - `limit` (optional, default 20): Number of results
- **Examples:**
  - Search for song "Ishq":
    ```bash
    curl "https://ytmusicapi-worker.<your-subdomain>.workers.dev/search?q=Ishq&filter=songs"
    ```
  - Search for "Radiohead" songs:
    ```bash
    curl "https://ytmusicapi-worker.<your-subdomain>.workers.dev/search?q=Radiohead&filter=songs"
    ```

### 3. Search Suggestions
- **Endpoint:** `GET /search/suggestions?q=<query>`
- **Example:**
  ```bash
  curl "https://ytmusicapi-worker.<your-subdomain>.workers.dev/search/suggestions?q=Coldplay"
  ```

### 4. Artist Details
- **Endpoint:** `GET /artist?id=<channelId>`
- **Example:**
  ```bash
  curl "https://ytmusicapi-worker.<your-subdomain>.workers.dev/artist?id=UC1LI9S-h1HDCzK3z346p4rA"
  ```

### 5. Album Details
- **Endpoint:** `GET /album?id=<browseId>`
- **Example:**
  ```bash
  curl "https://ytmusicapi-worker.<your-subdomain>.workers.dev/album?id=MPREb_953CFFR0aYf"
  ```

### 6. Playlist Details
- **Endpoint:** `GET /playlist?id=<playlistId>&limit=<number>`
- **Example:**
  ```bash
  curl "https://ytmusicapi-worker.<your-subdomain>.workers.dev/playlist?id=RDCLAK5uy_kwbRAn"
  ```

### 7. Song Details
- **Endpoint:** `GET /song?id=<videoId>`
- **Example:**
  ```bash
  curl "https://ytmusicapi-worker.<your-subdomain>.workers.dev/song?id=fJ9rUzIMcZQ"
  ```

### 8. Song Lyrics
- **Endpoint:** `GET /lyrics?id=<videoId_or_browseId>`
- **Example:**
  ```bash
  curl "https://ytmusicapi-worker.<your-subdomain>.workers.dev/lyrics?id=fJ9rUzIMcZQ"
  ```

### 9. Charts
- **Endpoint:** `GET /charts?country=<countryCode>`
- **Example:**
  ```bash
  curl "https://ytmusicapi-worker.<your-subdomain>.workers.dev/charts?country=US"
  ```

### 10. Watch Playlist / Radio
- **Endpoint:** `GET /watch?id=<videoId>`
- **Example:**
  ```bash
  curl "https://ytmusicapi-worker.<your-subdomain>.workers.dev/watch?id=fJ9rUzIMcZQ"
  ```

---

## Authentication (Optional)

For private features or user library management, configure your authentication cookie/oauth JSON as a Cloudflare Worker secret:

```bash
npx wrangler secret put YT_AUTH
```

Paste your `oauth.json` or headers JSON string when prompted. The Worker will automatically use this credential for requests.
