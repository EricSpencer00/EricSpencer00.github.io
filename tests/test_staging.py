import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from apply_ga4 import TAG
from prepare_staging import prepare, check, transform


class StagingTests(unittest.TestCase):
    def test_every_generated_page_loses_analytics_and_keeps_canonical(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('index.html', 'projects/work/index.html', 'apps/work/index.html'):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('<html><head><link rel="canonical" href="https://ericspencer.us/">' + TAG + '</head><body><script>const app = 1;</script></body></html>')
            (root / 'sitemap.xml').write_text('production')
            prepare(root)
            self.assertEqual(check(root), [])
            for path in root.rglob('*.html'):
                self.assertIn('https://ericspencer.us/', path.read_text())
                self.assertIn('const app = 1;', path.read_text())
                self.assertNotIn('G-30FQRTZWJ8', path.read_text())
            original = (root / 'index.html').read_text()
            prepare(root)
            self.assertEqual((root / 'index.html').read_text(), original)

    def test_check_rejects_analytics_in_javascript_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prepare(root)
            (root / 'app.js').write_text("gtag('config', 'G-30FQRTZWJ8');")
            self.assertTrue(any('analytics' in p for p in check(root)))

    def test_existing_robots_variants_and_uppercase_head(self):
        text = "<HEAD><META content='index,follow' name='robots'></HEAD>"
        transformed = transform(text)
        self.assertIn('noindex, follow', transformed)
        self.assertNotIn("index,follow", transformed)
        self.assertEqual(transformed, transform(transformed))
