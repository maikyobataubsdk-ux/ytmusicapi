import json
from urllib.parse import parse_qs, urlparse

try:
    import pyodide_http

    pyodide_http.patch_all()
except (ImportError, AttributeError):
    pass

try:
    from pyodide.ffi import to_js
except (ImportError, AttributeError):
    try:
        from pyodide import to_js  # type: ignore[no-redef]
    except (ImportError, AttributeError):

        def to_js(obj, **kwargs):  # type: ignore[misc]
            return obj


try:
    from js import Headers, Response
except (ImportError, AttributeError):

    class Headers:  # type: ignore[no-redef]
        @staticmethod
        def new(headers_dict):
            return headers_dict

    class Response:  # type: ignore[no-redef]
        def __init__(self, body, status=200, headers=None):
            self.body = body
            self.status = status
            self.headers = headers or {}

        @staticmethod
        def new(body, status=200, headers=None):
            if isinstance(status, dict):
                options = status
                return Response(
                    body,
                    status=options.get("status", 200),
                    headers=options.get("headers"),
                )
            return Response(body, status=status, headers=headers)


from ytmusicapi import YTMusic

# Global instance for performance across worker requests
yt_instance = None


def get_yt_instance(auth_data=None):
    global yt_instance
    if auth_data and str(auth_data) != "undefined":
        if isinstance(auth_data, str):
            try:
                auth_data = json.loads(auth_data)
            except Exception:  # noqa: S110, BLE001
                pass
        return YTMusic(auth_data)
    if yt_instance is None:
        yt_instance = YTMusic()
    return yt_instance


def json_response(data, status=200):
    headers_dict = {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-YT-Auth",
    }
    options = to_js({"status": status, "headers": to_js(headers_dict)})
    return Response.new(json.dumps(data, ensure_ascii=False), options)


def error_response(message, status=400):
    return json_response({"error": str(message)}, status=status)


async def on_fetch(request, env):
    # Handle CORS preflight
    if request.method == "OPTIONS":
        headers_dict = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-YT-Auth",
        }
        options = to_js({"status": 204, "headers": to_js(headers_dict)})
        return Response.new("", options)

    try:
        url = urlparse(request.url)
        path = url.path.rstrip("/")
        query = parse_qs(url.query)

        def get_param(name, default=None):
            val = query.get(name)
            return val[0] if val else default

        # Optional auth configured via env variable YT_AUTH or header X-YT-Auth
        auth_data = getattr(env, "YT_AUTH", None)
        yt = get_yt_instance(auth_data)

        if path in ("", "/"):
            return json_response(
                {
                    "status": "ok",
                    "service": "ytmusicapi Cloudflare Worker",
                    "endpoints": {
                        "/search?q=query[&filter=songs|videos|albums|artists|playlists]": "Search YouTube Music",
                        "/search/suggestions?q=query": "Get search suggestions",
                        "/artist?id=channelId": "Get artist details and releases",
                        "/album?id=browseId": "Get album details and tracks",
                        "/playlist?id=playlistId[&limit=100]": "Get playlist details and items",
                        "/song?id=videoId": "Get song metadata",
                        "/lyrics?id=browseId": "Get lyrics for a song or browseId",
                        "/charts[?country=US]": "Get music charts",
                        "/watch?id=videoId": "Get watch playlist and recommended next songs",
                    },
                }
            )

        elif path == "/search":
            q = get_param("q")
            if not q:
                return error_response("Missing required parameter 'q'", 400)
            filter_param = get_param("filter")
            limit = int(get_param("limit", 20))
            ignore_spelling = get_param("ignore_spelling", "false").lower() == "true"
            results = yt.search(
                q,
                filter=filter_param,
                limit=limit,
                ignore_spelling=ignore_spelling,
            )
            return json_response(results)

        elif path == "/search/suggestions":
            q = get_param("q")
            if not q:
                return error_response("Missing required parameter 'q'", 400)
            detailed = get_param("detailed", "false").lower() == "true"
            suggestions = yt.get_search_suggestions(q, detailed=detailed)
            return json_response(suggestions)

        elif path == "/artist":
            artist_id = get_param("id")
            if not artist_id:
                return error_response("Missing required parameter 'id'", 400)
            artist = yt.get_artist(artist_id)
            return json_response(artist)

        elif path == "/album":
            album_id = get_param("id")
            if not album_id:
                return error_response("Missing required parameter 'id'", 400)
            album = yt.get_album(album_id)
            return json_response(album)

        elif path == "/playlist":
            playlist_id = get_param("id")
            if not playlist_id:
                return error_response("Missing required parameter 'id'", 400)
            limit = int(get_param("limit", 100))
            playlist = yt.get_playlist(playlist_id, limit=limit)
            return json_response(playlist)

        elif path == "/song":
            video_id = get_param("id")
            if not video_id:
                return error_response("Missing required parameter 'id'", 400)
            song = yt.get_song(video_id)
            return json_response(song)

        elif path == "/lyrics":
            lyrics_id = get_param("id")
            if not lyrics_id:
                return error_response("Missing required parameter 'id'", 400)
            if not lyrics_id.startswith("MPLY"):
                try:
                    watch_playlist = yt.get_watch_playlist(videoId=lyrics_id)
                    lyrics_id = watch_playlist.get("lyrics")
                except Exception:  # noqa: BLE001, S110
                    pass
            if not lyrics_id:
                return error_response("Lyrics not found for this track", 404)
            lyrics = yt.get_lyrics(lyrics_id)
            return json_response(lyrics)

        elif path == "/charts":
            country = get_param("country", "ZZ")
            charts = yt.get_charts(country=country)
            return json_response(charts)

        elif path == "/watch":
            video_id = get_param("id")
            playlist_id = get_param("playlist_id")
            if not video_id and not playlist_id:
                return error_response("Missing required parameter 'id' or 'playlist_id'", 400)
            watch = yt.get_watch_playlist(videoId=video_id, playlistId=playlist_id)
            return json_response(watch)

        else:
            return error_response("Endpoint not found", 404)

    except Exception as e:  # noqa: BLE001
        return error_response(str(e), 500)
