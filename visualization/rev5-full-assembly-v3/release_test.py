"""Portable byte/closure/media checks; no private Git history or native rendering."""
import base64
import gzip
import hashlib
import html.parser
import json
import pathlib
import shutil
import struct
import subprocess
import unittest
from fractions import Fraction
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parent
MEDIA = json.loads((ROOT / "media-manifest.json").read_text())
SOURCE_HASHES = {
    "scene-data.js": "8f55ba45dcd688c0253ec7c81628ce0ccedf7cedd79e7752191f2d8978eeedd0",
    "edge-data.js": "ecec1cd659ed4ca66e1d0126acb9c0ec1e638a927a57fc50bb3d8253d4c35e8b",
    "inventory.json": "3caf94d95eedaef9f657be31b7e82cfce22a4b96a262d184249790026c2dd9ba",
    "interactive-viewer.js": "936a6eedfdd8b09fe873beee30f1d11f7f1be111076aafd26b278200a7a01833",
    "drawings.js": "7c8719441b48de3c3a8f86c2abb522a6da97ccaeb4afba62cfdb5212817dab95",
    "features.js": "a2370e219c8e80c1bbee3546fda5401885cfb7d88568faaab7a7b4b60d17d3da",
    "viewer.js": "244375de1c04f7c5b6cc611552ed1cb4305114969a9ce8d32d51109fdf70e89c",
    "presentation-plan.json": "941aba63dac8ff7ecc5ce67c09be99afabc6037193b418ef6183ffe163c802af",
    "plan-data.js": "05ed439f1bc2aed8cccc0d75d9b38d299a27abcb24ecafad5070086e57a6e6f1",
    "runtime-assets.json": "7233e5dfe0344b255733d38ce83fd881ff6b2da5ef1a5a294a7b94749de30b96",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []
        self.csp = None
        self.videos = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        for name in ("src", "href", "poster"):
            if name in attrs:
                self.assets.append(attrs[name])
        if tag == "meta" and attrs.get("http-equiv") == "Content-Security-Policy":
            self.csp = attrs["content"]
        if tag == "video":
            self.videos.append(attrs)


class ReleaseTests(unittest.TestCase):
    def test_frozen_core_is_byte_identical(self):
        for name, expected in SOURCE_HASHES.items():
            with self.subTest(asset=name):
                self.assertEqual(digest((ROOT / name).read_bytes()), expected)

    def test_all_399_packed_source_streams(self):
        text = (ROOT / "scene-data.js").read_text()
        scene = json.loads(text.removeprefix("globalThis.REV5_FULL_SCENE = ").rstrip().removesuffix(";"))
        inventory = json.loads((ROOT / "inventory.json").read_text())
        self.assertEqual({k: v for k, v in scene.items() if k != "payload"}, inventory)
        payload = gzip.decompress(base64.b64decode(scene["payload"], validate=True))
        self.assertEqual(digest(payload), scene["payload_sha256"])
        self.assertEqual(len(payload), scene["payload_bytes"])
        self.assertEqual(len(scene["components"]), 399)
        self.assertEqual(sum(part["triangles"] for part in scene["components"]), 794132)
        offset = 0
        for part in scene["components"]:
            self.assertEqual(part["offset"], offset)
            count = part["coordinate_count"] * 8
            self.assertEqual(count, part["triangles"] * 9 * 8)
            self.assertEqual(digest(payload[offset:offset + count]), part["position_sha256"])
            offset += count
        self.assertEqual(offset, len(payload))

    def test_local_closure_and_minimal_csp(self):
        page = Page()
        page.feed((ROOT / "index.html").read_text())
        self.assertEqual(page.csp, "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self'; connect-src 'none'; base-uri 'none'; form-action 'none'")
        for asset in page.assets:
            parsed = urlsplit(asset)
            if parsed.scheme == "data" or not parsed.path:
                continue
            self.assertFalse(parsed.scheme or parsed.netloc, asset)
            path = (ROOT / parsed.path).resolve()
            self.assertTrue(path.is_relative_to(ROOT), asset)
            self.assertTrue(path.is_file(), asset)
        self.assertEqual(len(page.videos), 1)
        self.assertIn("controls", page.videos[0])
        self.assertEqual(page.videos[0]["preload"], "metadata")
        self.assertNotIn("autoplay", page.videos[0])
        self.assertNotIn("loop", page.videos[0])
        for clip in MEDIA["clips"]:
            for kind in ("video", "poster"):
                path = (ROOT / clip[kind]["path"]).resolve()
                self.assertTrue(path.is_relative_to(ROOT / "media"))
                self.assertTrue(path.is_file())

    def test_original_media_bytes_and_posters(self):
        self.assertEqual(len(MEDIA["clips"]), 6)
        expected = set()
        for clip in MEDIA["clips"]:
            for kind in ("video", "poster"):
                asset = clip[kind]
                data = (ROOT / asset["path"]).read_bytes()
                self.assertEqual(digest(data), asset["sha256"])
                expected.add(pathlib.PurePosixPath(asset["path"]).name)
                if kind == "video":
                    self.assertEqual(len(data), asset["bytes"])
                else:
                    self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                    self.assertEqual(list(struct.unpack(">II", data[16:24])), asset["dimensions"])
        self.assertEqual({p.name for p in (ROOT / "media").iterdir()}, expected)

    @unittest.skipUnless(shutil.which("ffprobe") and shutil.which("ffmpeg"), "Existing ffprobe/ffmpeg required for actual media decode")
    def test_actual_media_metadata_packets_and_all_decoded_frames(self):
        for clip in MEDIA["clips"]:
            with self.subTest(clip=clip["id"]):
                video = clip["video"]
                path = str(ROOT / video["path"])
                info = json.loads(subprocess.check_output([
                    "ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format",
                    "-of", "json", path,
                ], timeout=60))
                self.assertEqual(len(info["streams"]), 1)
                stream = info["streams"][0]
                self.assertEqual(stream["codec_name"], video["codec"])
                self.assertEqual(stream["pix_fmt"], video["pixel_format"])
                self.assertEqual([stream["width"], stream["height"]], [960, 640])
                self.assertEqual(int(stream["nb_read_frames"]), video["frames"])
                self.assertEqual(Fraction(stream["r_frame_rate"]), 12)
                self.assertEqual(float(stream["duration"]), video["duration_seconds"])
                self.assertEqual(float(info["format"]["duration"]), video["container_duration_seconds"])
                if video["packet_timing"] is not None:
                    timing = video["packet_timing"]
                    packets = json.loads(subprocess.check_output([
                        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_packets",
                        "-show_entries", "packet=pts,duration", "-of", "json", path,
                    ], timeout=60))["packets"]
                    packets.sort(key=lambda packet: packet["pts"])
                    self.assertEqual([p["pts"] for p in packets], [i * 1024 for i in range(145)])
                    self.assertTrue(all(p["duration"] == 1024 for p in packets))
                    self.assertEqual(stream["time_base"], timing["time_base"])
                    end = packets[-1]["pts"] + packets[-1]["duration"]
                    self.assertEqual(end, timing["packet_end_ticks"])
                    self.assertEqual(stream["duration_ts"] - end, timing["stream_minus_packet_end_ticks"])
                decoded = subprocess.check_output([
                    "ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-threads", "1",
                    "-i", path, "-map", "0:v:0", "-f", "framemd5", "-",
                ], text=True, timeout=60)
                frames = [line for line in decoded.splitlines() if line and not line.startswith("#")]
                self.assertEqual(len(frames), video["frames"])
                self.assertEqual(digest((ROOT / video["path"]).read_bytes()), video["sha256"])


if __name__ == "__main__":
    unittest.main()
