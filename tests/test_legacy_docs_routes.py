"""Keep the seven known broken document roots usable and out of the sitemap."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_site import PageParser


class LegacyDocumentRoutesTests(unittest.TestCase):
    def test_known_document_roots_point_to_their_existing_project_pages(self):
        sitemap = (ROOT / "sitemap.xml").read_text()
        for name in ("certification", "failure-model", "language-reference", "memory-model",
                     "module-system", "no-std", "stdlib-portability"):
            html = (ROOT / name / "index.html").read_text()
            parser = PageParser()
            parser.feed(html)
            target = "https://ericspencer.us/Resilient/" + name
            self.assertEqual(set(parser.canonicals), {target})
            self.assertEqual(html.count('<link rel="canonical"'), 1)
            self.assertIn('content="noindex, follow"', html)
            self.assertIn(f'content="0; url=/Resilient/{name}"', html)
            self.assertNotIn(f"<loc>https://ericspencer.us/{name}/</loc>", sitemap)
        self.assertFalse((ROOT / "unknown-document" / "index.html").exists())


if __name__ == "__main__":
    unittest.main()
