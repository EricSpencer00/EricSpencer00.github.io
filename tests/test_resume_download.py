"""The stable download follows the same edition as the résumé landing page."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_resume_pages


class ResumeDownloadTest(unittest.TestCase):
    def test_download_tracks_pin_and_recency_fallback(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            content = root / "content"
            content.mkdir()
            pdfs = root / "assets" / "pdf"
            pdfs.mkdir(parents=True)
            (content / "resumes.txt").write_text(
                "resume/110126|reviewed.pdf|Resume|Reviewed edition|no\n"
                "resume/110226|newer.pdf|Resume|Newer edition|no\n",
                encoding="utf-8",
            )
            (pdfs / "reviewed.pdf").write_bytes(b"reviewed PDF bytes")
            (pdfs / "newer.pdf").write_bytes(b"newer PDF bytes")
            pin = content / "resume-current.txt"
            pin.write_text("resume/110126\n", encoding="utf-8")
            download = root / "assets" / "resume.pdf"
            download.write_bytes(b"obsolete PDF bytes")
            landing = root / "resume" / "index.html"

            with patch.object(build_resume_pages, "ROOT", root), patch.object(
                build_resume_pages, "CONTENT", content
            ):
                build_resume_pages.main()
                self.assertEqual(download.read_bytes(), (pdfs / "reviewed.pdf").read_bytes())
                self.assertIn('location.replace("/resume/110126/")', landing.read_text())

                pin.unlink()
                build_resume_pages.main()
                self.assertEqual(download.read_bytes(), (pdfs / "newer.pdf").read_bytes())
                self.assertIn('location.replace("/resume/110226/")', landing.read_text())
