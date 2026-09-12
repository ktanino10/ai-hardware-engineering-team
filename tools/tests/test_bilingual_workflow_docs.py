"""Public reader navigation checks; no CAD, design regeneration or network."""
import html.parser
import json
import pathlib
import re
import shutil
import subprocess
import unittest
import urllib.parse


ROOT = pathlib.Path(__file__).resolve().parents[2]
INVENTORY = json.loads((ROOT / "docs/language-coverage.json").read_text(encoding="utf-8"))


def edition_paths():
    pairs = INVENTORY["entry_points"] + INVENTORY["new_pairs"]
    return {pair[lang] for pair in pairs for lang in ("en", "ja")}


def without_fences(text):
    return re.sub(r"^```.*?^```[^\n]*", "", text, flags=re.MULTILINE | re.DOTALL)


def anchors(text):
    counts = {}
    result = set()
    for title in re.findall(r"^#{1,6}\s+(.+)", without_fences(text), re.MULTILINE):
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(f"{slug}-{count}" if count else slug)
    return result


class Page(html.parser.HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.lang = None
        self.links = []
        self.local_assets = []
        self.has_main = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "main":
            self.has_main = True
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "link":
            self.local_assets.append(attrs.get("href", ""))


class BilingualWorkflowDocsTests(unittest.TestCase):
    def test_inventory_has_unique_sources_and_real_language_destinations(self):
        sources = [row["source"] for row in INVENTORY["entry_points"]]
        self.assertEqual(len(sources), len(set(sources)))
        self.assertRegex(INVENTORY["source_revision"], r"^[0-9a-f]{40}$")
        self.assertEqual(INVENTORY["source_revision"], INVENTORY["config_revision"])
        for row in INVENTORY["entry_points"]:
            with self.subTest(source=row["source"]):
                self.assertIn(row["kind"], {"translation", "reading-edition"})
                self.assertNotEqual(row["en"], row["ja"])
                for key in ("source", "en", "ja"):
                    self.assertTrue((ROOT / row[key]).is_file(), row[key])
                japanese = (ROOT / row["ja"]).read_text(encoding="utf-8")
                self.assertRegex(japanese, r"[\u3040-\u30ff]")

    def test_every_reader_readme_and_markdown_path_is_classified(self):
        tracked = subprocess.run(
            ["git", "ls-files", "-z", "*.md"], cwd=ROOT,
            check=True, capture_output=True, text=True,
        ).stdout.split("\0")
        sources = {row["source"] for row in INVENTORY["entry_points"]}
        editions = edition_paths()
        references = set(INVENTORY["shared_reference_paths"])
        prefixes = tuple(
            INVENTORY["shared_machine_policy_prefixes"]
            + INVENTORY["shared_engineering_record_prefixes"]
        )
        for name in filter(None, tracked):
            with self.subTest(path=name):
                if pathlib.PurePosixPath(name).name == "README.md":
                    self.assertIn(name, sources | editions)
                self.assertTrue(
                    name in sources | editions | references or name.startswith(prefixes),
                    f"Unclassified Markdown: {name}",
                )

    def test_local_links_and_fragments_in_reader_editions(self):
        # Original domain ledgers retain their historical prose unchanged.
        paths = {p for p in edition_paths() if p.startswith("docs/") or "/" not in p}
        for name in sorted(paths):
            path = ROOT / name
            text = without_fences(path.read_text(encoding="utf-8"))
            for target in re.findall(r"\[[^\]]+\]\(([^)\s]+)\)", text):
                parsed = urllib.parse.urlsplit(target)
                if parsed.scheme or parsed.netloc:
                    continue
                destination = (path.parent / urllib.parse.unquote(parsed.path)).resolve()
                if not parsed.path:
                    destination = path
                with self.subTest(page=name, target=target):
                    self.assertTrue(destination.is_relative_to(ROOT))
                    self.assertTrue(destination.exists(), target)
                    if destination.suffix == ".md" and parsed.fragment:
                        self.assertIn(
                            urllib.parse.unquote(parsed.fragment),
                            anchors(destination.read_text(encoding="utf-8")),
                        )

    def test_pages_routes_stay_inside_uploaded_directory(self):
        pages_root = ROOT / "visualization"
        for lang, filename, other in (
            ("en", "index.html", "index.ja.html"),
            ("ja", "index.ja.html", "index.html"),
        ):
            page = Page((pages_root / filename).read_text(encoding="utf-8"))
            with self.subTest(lang=lang):
                self.assertEqual(page.lang, lang)
                self.assertTrue(page.has_main)
                self.assertIn(other, page.links)
                self.assertIn(f"dashboard/index.html?lang={lang}", page.links)
                for target in page.links + page.local_assets:
                    url = urllib.parse.urlsplit(target)
                    if url.scheme or url.netloc:
                        continue
                    path = (pages_root / url.path).resolve()
                    self.assertTrue(path.is_relative_to(pages_root), target)
                    self.assertTrue(path.is_file(), target)

    @unittest.skipUnless(shutil.which("node"), "Node unavailable: dashboard VM check not run")
    def test_dashboard_language_behavior(self):
        result = subprocess.run(
            ["node", "tools/tests/test_dashboard_i18n.cjs"], cwd=ROOT,
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
