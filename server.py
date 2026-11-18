#!/usr/bin/env python3
"""Pi Bell Slapper web UI and HTTP API. Uses only the Python standard library."""

import argparse
import gzip
import json
import re
import shutil
import subprocess
import tempfile
import threading
import time
import wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent

MIN_INTERVAL = 1.0  # Hard rate limit: never more than one ding per second.
MAX_INTERVAL = 10.0
MAX_COUNT = 10
PULSE = 0.01  # Solenoid on-time per ding, in seconds.
SOUND_DELAY = 1.0  # Pause between the last ding and the sound.
MAX_SOUND_SECONDS = 10.0
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_SOUNDS = 50
MAX_JSON_BYTES = 4096
NAME_RE = re.compile(r'^[a-z0-9][a-z0-9_-]{0,39}$')

# Allowed upload extension -> (forced ffmpeg demuxer, magic byte check).
FORMATS = {
    'wav': ('wav', lambda b: b[:4] == b'RIFF' and b[8:12] == b'WAVE'),
    'aif': ('aiff', lambda b: b[:4] == b'FORM' and b[8:12] in (b'AIFF', b'AIFC')),
    'aiff': ('aiff', lambda b: b[:4] == b'FORM' and b[8:12] in (b'AIFF', b'AIFC')),
    'mp3': ('mp3', lambda b: b[:3] == b'ID3' or (len(b) > 1 and b[0] == 0xFF and b[1] & 0xE0 == 0xE0)),
    'm4a': ('mov', lambda b: b[4:8] == b'ftyp'),
}

STATIC = {
    '/': ('index.html', 'text/html; charset=utf-8', 'no-cache'),
    '/app.js': ('app.js', 'text/javascript; charset=utf-8', 'no-cache'),
    '/bootstrap.min.css': ('bootstrap.min.css', 'text/css; charset=utf-8', 'max-age=604800'),
}


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


class Bell:
    def __init__(self, pin, dry_run):
        self.pin = pin
        self.lock = threading.Lock()
        self.last = 0.0
        self.gpio = None
        if not dry_run:
            import RPi.GPIO as GPIO
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
            self.gpio = GPIO

    def busy(self):
        return self.lock.locked()

    def start(self, count, interval, sound):
        """Run a ding sequence in the background. Returns False if one is already running."""
        if not self.lock.acquire(blocking=False):
            return False
        threading.Thread(target=self._run, args=(count, interval, sound), daemon=True).start()
        return True

    def _run(self, count, interval, sound):
        try:
            for i in range(count):
                gap = max(MIN_INTERVAL, interval) if i else MIN_INTERVAL
                time.sleep(max(0.0, self.last + gap - time.monotonic()))
                self._slap()
            if sound:
                time.sleep(SOUND_DELAY)
                subprocess.run(['aplay', '-q', str(sound)], timeout=MAX_SOUND_SECONDS + 5,
                               stdin=subprocess.DEVNULL)
        except Exception as e:
            print(f'Ding failed: {e}', flush=True)
        finally:
            self.lock.release()

    def _slap(self):
        if self.gpio:
            self.gpio.output(self.pin, self.gpio.HIGH)
            time.sleep(PULSE)
            self.gpio.output(self.pin, self.gpio.LOW)
        else:
            print('DING (dry run)', flush=True)
        self.last = time.monotonic()


class Sounds:
    def __init__(self, data_dir):
        self.dir = data_dir / 'sounds'
        self.dir.mkdir(parents=True, exist_ok=True)
        self.upload_lock = threading.Lock()  # One transcode at a time; the Pi Zero is slow.
        if not self.list():
            shutil.copy(ROOT / 'ding.wav', self.dir / 'ding.wav')

    def list(self):
        return sorted(p.stem for p in self.dir.glob('*.wav'))

    def path(self, name):
        if isinstance(name, str) and NAME_RE.match(name):
            p = self.dir / f'{name}.wav'
            if p.is_file():
                return p
        return None

    def delete(self, name):
        p = self.path(name)
        if not p:
            raise ApiError(404, 'Sound not found.')
        p.unlink()

    def add(self, filename, data):
        """Validate an upload and transcode it to a 48 kHz stereo WAV. Original bytes are never kept."""
        stem, _, ext = filename.lower().rpartition('.')
        if not stem or ext not in FORMATS:
            raise ApiError(400, 'Sound must be a .wav, .aiff, .mp3, or .m4a file.')
        demuxer, magic_ok = FORMATS[ext]
        if not magic_ok(data[:12]):
            raise ApiError(400, f'File contents are not a valid .{ext} file.')
        name = re.sub(r'[^a-z0-9_-]+', '-', stem).strip('-_')[:40] or 'sound'
        if self.path(name):
            raise ApiError(409, f'A sound named "{name}" already exists.')
        if len(self.list()) >= MAX_SOUNDS:
            raise ApiError(400, f'Sound limit ({MAX_SOUNDS}) reached. Delete one first.')

        with tempfile.TemporaryDirectory(dir=self.dir.parent) as tmp:
            src, out = Path(tmp, 'upload'), Path(tmp, 'out.wav')
            src.write_bytes(data)
            # Forced demuxer + file-only protocol stops ffmpeg from following playlists or URLs.
            cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-protocol_whitelist', 'file',
                   '-f', demuxer, '-i', str(src), '-map', '0:a:0', '-t', str(MAX_SOUND_SECONDS + 0.5),
                   '-ac', '2', '-ar', '48000', '-c:a', 'pcm_s16le', '-f', 'wav', str(out)]
            try:
                subprocess.run(cmd, capture_output=True, timeout=60, check=True)
                with wave.open(str(out)) as w:
                    seconds = w.getnframes() / w.getframerate()
            except (subprocess.SubprocessError, OSError, wave.Error, EOFError, ZeroDivisionError):
                raise ApiError(400, 'Could not read audio from that file.')
            if seconds <= 0 or seconds > MAX_SOUND_SECONDS:
                raise ApiError(400, f'Sound must be {MAX_SOUND_SECONDS:g} seconds or less.')
            out.replace(self.dir / f'{name}.wav')
        return name


class Settings:
    def __init__(self, data_dir, sounds):
        self.file = data_dir / 'settings.json'
        self.sounds = sounds
        self.lock = threading.Lock()
        self.data = {'interval': 1.0, 'sound': 'ding'}
        try:
            self.update(json.loads(self.file.read_text()))
        except (OSError, ValueError, ApiError):
            pass

    def get(self):
        if not self.sounds.path(self.data['sound']):
            self.data['sound'] = next(iter(self.sounds.list()), '')
        return dict(self.data)

    def update(self, params):
        new = {}
        if 'interval' in params:
            new['interval'] = parse_interval(params['interval'])
        if 'sound' in params:
            if not self.sounds.path(params['sound']):
                raise ApiError(400, 'Unknown sound.')
            new['sound'] = params['sound']
        with self.lock:
            self.data.update(new)
            tmp = self.file.with_suffix('.tmp')
            tmp.write_text(json.dumps(self.data))
            tmp.replace(self.file)
        return self.get()


def parse_interval(value):
    try:
        interval = round(float(value), 2)
    except (TypeError, ValueError):
        interval = -1
    if not MIN_INTERVAL <= interval <= MAX_INTERVAL:
        raise ApiError(400, f'Interval must be between {MIN_INTERVAL:.2f} and {MAX_INTERVAL:.2f} seconds.')
    return interval


def parse_bool(value):
    return value is True or str(value).lower() in ('1', 'true', 'yes', 'on')


class Handler(BaseHTTPRequestHandler):
    server_version = 'BellSlapper'
    app = None  # Set in main().

    def do_GET(self):
        self.handle_request(self.route_get)

    def do_POST(self):
        self.handle_request(self.route_write)

    def do_PUT(self):
        self.handle_request(self.route_write)

    def do_DELETE(self):
        self.handle_request(self.route_write)

    def handle_request(self, route):
        url = urlsplit(self.path)
        self.url_path = url.path
        self.query = {k: v[-1] for k, v in parse_qs(url.query).items()}
        try:
            route()
        except ApiError as e:
            self.send_json({'error': str(e)}, e.status)

    def route_get(self):
        app = self.app
        if self.url_path == '/api/status':
            return self.send_json({'busy': app['bell'].busy(), 'settings': app['settings'].get(),
                                   'sounds': app['sounds'].list()})
        if self.url_path in STATIC:
            return self.send_static(self.url_path)
        raise ApiError(404, 'Not found.')

    def route_write(self):
        # Block cross-site browser requests; clients without an Origin header (curl, scripts) are fine.
        origin = self.headers.get('Origin')
        if origin and urlsplit(origin).netloc != self.headers.get('Host'):
            raise ApiError(403, 'Cross-origin request blocked.')

        app, method, path = self.app, self.command, self.url_path
        if method == 'POST' and path == '/api/ding':
            params = self.params()
            count = params.get('count', 1)
            if not str(count).isdigit() or not 1 <= int(count) <= MAX_COUNT:
                raise ApiError(400, f'Count must be between 1 and {MAX_COUNT}.')
            settings = app['settings'].get()
            interval = parse_interval(params['interval']) if 'interval' in params else settings['interval']
            sound = None
            if parse_bool(params.get('sound')):
                sound = app['sounds'].path(params.get('sound_name', settings['sound']))
                if not sound:
                    raise ApiError(400, 'No sound available. Upload one first.')
            if not app['bell'].start(int(count), interval, sound):
                raise ApiError(429, 'The bell is busy. Try again in a moment.')
            return self.send_json({'count': int(count), 'interval': interval, 'sound': bool(sound)}, 202)
        if method in ('POST', 'PUT') and path == '/api/settings':
            return self.send_json(app['settings'].update(self.params()))
        if method == 'POST' and path == '/api/sounds':
            return self.upload()
        if method == 'DELETE' and path.startswith('/api/sounds/'):
            app['sounds'].delete(path.removeprefix('/api/sounds/'))
            return self.send_json({'sounds': app['sounds'].list(), 'settings': app['settings'].get()})
        raise ApiError(404, 'Not found.')

    def upload(self):
        length = self.content_length()
        if length > MAX_UPLOAD_BYTES:
            self.close_connection = True
            raise ApiError(413, f'File is larger than {MAX_UPLOAD_BYTES // 1048576} MB.')
        sounds = self.app['sounds']
        if not sounds.upload_lock.acquire(blocking=False):
            self.close_connection = True
            raise ApiError(429, 'Another upload is in progress.')
        try:
            name = sounds.add(self.query.get('name', ''), self.rfile.read(length))
        finally:
            sounds.upload_lock.release()
        return self.send_json({'name': name, 'sounds': sounds.list()}, 201)

    def content_length(self):
        try:
            return int(self.headers.get('Content-Length', 0))
        except ValueError:
            raise ApiError(400, 'Invalid Content-Length.')

    def params(self):
        """Query string parameters, overridden by a JSON body if present."""
        params = dict(self.query)
        length = self.content_length()
        if length:
            if length > MAX_JSON_BYTES:
                self.close_connection = True
                raise ApiError(413, 'Request body too large.')
            try:
                body = json.loads(self.rfile.read(length))
            except ValueError:
                raise ApiError(400, 'Body must be JSON.')
            if not isinstance(body, dict):
                raise ApiError(400, 'Body must be a JSON object.')
            params.update(body)
        return params

    def send_json(self, data, status=200):
        self.send_body(json.dumps(data).encode(), 'application/json', status, 'no-store')

    def send_static(self, path):
        body, gz, content_type, cache = self.app['static'][path]
        if gz and 'gzip' in self.headers.get('Accept-Encoding', ''):
            self.send_body(gz, content_type, 200, cache, gzipped=True)
        else:
            self.send_body(body, content_type, 200, cache)

    def send_body(self, body, content_type, status, cache, gzipped=False):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', cache)
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; img-src 'self' data:")
        if gzipped:
            self.send_header('Content-Encoding', 'gzip')
            self.send_header('Vary', 'Accept-Encoding')
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description='Pi Bell Slapper web UI and API.')
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=80)
    parser.add_argument('--pin', type=int, default=4, help='BCM GPIO pin driving the solenoid')
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data', help='Settings and uploaded sounds')
    parser.add_argument('--dry-run', action='store_true', help='Print dings instead of using GPIO')
    args = parser.parse_args()

    args.data_dir.mkdir(parents=True, exist_ok=True)
    sounds = Sounds(args.data_dir)
    static = {}
    for path, (name, content_type, cache) in STATIC.items():
        body = (ROOT / 'web' / name).read_bytes()
        static[path] = (body, gzip.compress(body) if len(body) > 1024 else None, content_type, cache)
    Handler.app = {'bell': Bell(args.pin, args.dry_run), 'sounds': sounds,
                   'settings': Settings(args.data_dir, sounds), 'static': static}

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f'Bell Slapper listening on http://{args.host}:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        bell = Handler.app['bell']
        if bell.gpio:
            bell.gpio.cleanup()


if __name__ == '__main__':
    main()
