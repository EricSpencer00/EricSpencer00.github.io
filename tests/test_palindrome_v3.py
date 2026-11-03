"""Run the product correctness gates in the existing Python deploy suite."""
from pathlib import Path
import shutil,subprocess,unittest

class PalindromeV3Tests(unittest.TestCase):
 def test_phrase_search_and_client_gates(self):
  node=shutil.which('node')
  self.assertIsNotNone(node,'Node is required for palindrome phrase-search checks')
  result=subprocess.run([node,'--test','tests/palindrome-v3.test.mjs'],cwd=Path(__file__).resolve().parents[1],text=True,capture_output=True,timeout=30)
  self.assertEqual(result.returncode,0,result.stdout+result.stderr)
