"""Keep shared cards aligned with local and separately deployed pages."""
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import apply_og_tags
import build_og_images
import build_project_routes
import build_social_cards
import check_site


class SocialCardCandidatesTests(unittest.TestCase):
    def candidates(self, root, paths, apps=()):
        with patch.object(build_social_cards, 'ROOT', root), \
                patch.object(check_site, 'ROOT', root), \
                patch.object(build_social_cards, 'page_files', return_value=paths), \
                patch.object(build_social_cards, 'load_apps', return_value=apps):
            return list(build_social_cards.candidates())

    def write_stub(self, root, canonical):
        path = root / 'legacy' / 'index.html'
        path.parent.mkdir()
        path.write_text(
            '<title>Legacy documentation</title>'
            '<meta name="robots" content="noindex, follow">'
            f'<link rel="canonical" href="{canonical}">'
            '<!-- redirect stub -->', encoding='utf-8',
        )
        return path

    def test_missing_project_target_gets_a_card_at_its_canonical_url(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            canonical = build_social_cards.SITE + '/Resilient/certification'
            stub = self.write_stub(root, canonical)
            self.assertEqual(self.candidates(root, [stub]), [
                (canonical, 'Legacy documentation', 'Legacy documentation'),
            ])

    def test_app_entry_uses_only_its_first_party_share_card(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            canonical = build_social_cards.SITE + '/separate-project/'
            app = {'slug': 'example', 'name': 'Example app',
                   'url': canonical, 'description': 'Use the example.'}
            stub = root / 'apps/example/index.html'
            stub.parent.mkdir(parents=True)
            stub.write_text(
                '<title>Example app | Eric Spencer</title>'
                '<meta name="robots" content="noindex, follow">'
                f'<link rel="canonical" href="{canonical}">'
                '<!-- redirect stub -->', encoding='utf-8',
            )
            self.assertFalse((root / 'separate-project/index.html').exists())
            self.assertEqual(self.candidates(root, [stub], [app]), [
                (build_social_cards.SITE + '/apps/example/', 'Example app', 'Use the example.'),
            ])

    def test_existing_local_target_supplies_one_card_without_the_stub(self):
        for relative in ('current/index.html', 'current.html'):
            with self.subTest(target=relative), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                canonical = build_social_cards.SITE + (
                    '/current/' if relative.endswith('/index.html') else '/current.html'
                )
                stub = self.write_stub(root, canonical)
                target.write_text(
                    '<title>Current documentation</title>'
                    '<meta name="description" content="Current reference.">'
                    f'<link rel="canonical" href="{canonical}">', encoding='utf-8',
                )
                # File URLs do not have their own card candidate, but still
                # count as a real canonical target when checking the stub.
                expected = [] if relative == 'current.html' else [
                    (canonical, 'Current documentation', 'Current reference.'),
                ]
                self.assertEqual(self.candidates(root, [stub, target]), expected)

    def test_published_pages_excludes_palindrome_authoring_templates(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            authoring = root / 'palindrome-v3' / 'canonical'
            authoring.mkdir(parents=True)
            for name in ('index.html', 'production-template.html'):
                (authoring / name).write_text('<title>Authoring</title>', encoding='utf-8')
            preview = root / 'palindrome-v3' / 'index.html'
            canonical = build_og_images.SITE + '/palindrome-v3/'
            preview.write_text(f'<link rel="canonical" href="{canonical}">', encoding='utf-8')
            with patch.object(build_og_images, 'ROOT', root), \
                    patch.object(build_og_images, 'EXTERNAL', []):
                self.assertEqual(build_og_images.published_pages(), {canonical: [preview]})

    def test_live_project_source_and_mount_keep_identical_share_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'projects/2026/stem-player/index.html'
            mount = root / 'stem-player/index.html'
            markup = '''<html><head>
<title>Moved player</title>
<meta name="description" content="The player moved.">
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="https://stemacle.com/">
</head><body></body></html>'''
            for path in (source, mount, root / 'apps/index.html'):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(markup, encoding='utf-8')
            cards = root / 'assets/og'
            cards.mkdir(parents=True)
            # Both names existed when the source and public mount diverged.
            for slug in ('stem-player', 'projects-2026-stem-player', 'projects'):
                (cards / f'{slug}.jpg').touch()
            with patch.object(apply_og_tags, 'ROOT', root), \
                    patch.object(apply_og_tags, 'OUT', cards), \
                    patch.object(build_project_routes, 'ROOT', root), \
                    patch.object(check_site, 'ROOT', root), \
                    patch.object(apply_og_tags, 'published_pages', return_value={}), \
                    patch.object(apply_og_tags, 'load_apps', return_value=[]), \
                    patch.object(apply_og_tags, 'page_files', return_value=[source, mount]), \
                    patch.object(sys, 'argv', ['apply_og_tags.py']), redirect_stdout(io.StringIO()):
                self.assertEqual(apply_og_tags.main(), 0)
            self.assertEqual(source.read_bytes(), mount.read_bytes())
            self.assertIn('/assets/og/stem-player.jpg', source.read_text())
            self.assertNotIn('/assets/og/projects-2026-stem-player.jpg', source.read_text())


if __name__ == '__main__':
    unittest.main()
