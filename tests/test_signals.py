import io
import json
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import collect_signals as collector
import build


class SignalTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.history, self.out = self.root / 'history.json', self.root / 'signals.json'
        daily = {date.today().isoformat(): {'views': 4, 'views_uniques': 2}}
        self.history.write_text(json.dumps({'generated': 'old', 'repos': {'EricSpencer00/denied': {'daily': daily}}}))
        self.out.write_text('existing')
        for name, value in [('HISTORY', self.history), ('OUT', self.out), ('ROOT', self.root), ('TOKEN', 'test-only'), ('OWNERS', ['EricSpencer00'])]:
            context = patch.object(collector, name, value)
            context.start()
            self.addCleanup(context.stop)

    def test_missing_token_preserves_files_without_network(self):
        before = self.history.read_bytes(), self.out.read_bytes()
        with patch.object(collector, 'TOKEN', ''), patch.object(collector, 'get') as get:
            collector.main()
        get.assert_not_called()
        self.assertEqual(before, (self.history.read_bytes(), self.out.read_bytes()))

    def test_no_accessible_repositories_preserves_snapshot(self):
        before = self.history.read_bytes(), self.out.read_bytes()
        with patch.object(collector, 'repos', return_value=[{'full_name': 'EricSpencer00/denied'}]), patch.object(collector, 'get', return_value=None):
            collector.main()
        self.assertEqual(before, (self.history.read_bytes(), self.out.read_bytes()))

    def test_denied_repo_history_is_retained_but_not_restamped_in_rollup(self):
        repos = [{'full_name': 'EricSpencer00/denied'}, {'full_name': 'EricSpencer00/fresh', 'name': 'fresh'}]
        traffic = {'views': [{'timestamp': date.today().isoformat(), 'count': 3, 'uniques': 2}]}
        with patch.object(collector, 'repos', return_value=repos), patch.object(collector, 'get', side_effect=[None, traffic, None]):
            collector.main()
        self.assertIn('EricSpencer00/denied', json.loads(self.history.read_text())['repos'])
        self.assertEqual(set(json.loads(self.out.read_text())['repos']), {'EricSpencer00/fresh'})

    def test_corrupt_history_and_api_failure_preserve_files(self):
        self.history.write_text('broken')
        with self.assertRaises(ValueError):
            collector.main()
        self.assertEqual(self.history.read_text(), 'broken')
        self.assertEqual(self.out.read_text(), 'existing')

    def test_api_failure_preserves_both_snapshots(self):
        before = self.history.read_bytes(), self.out.read_bytes()
        with patch.object(collector, 'repos', side_effect=RuntimeError('API failure')):
            with self.assertRaises(RuntimeError):
                collector.main()
        self.assertEqual(before, (self.history.read_bytes(), self.out.read_bytes()))

    def test_rate_limit_is_not_treated_as_missing_permission(self):
        error = urllib.error.HTTPError('https://api.github.com', 403, 'rate limit', {'X-RateLimit-Remaining': '0'}, io.BytesIO())
        with patch('urllib.request.urlopen', side_effect=error), self.assertRaises(urllib.error.HTTPError):
            collector.get('https://api.github.com', allow_denied=True)

    def test_browser_freshness_and_star_fallback(self):
        page = build.build_page('', '', '', '', '')
        start = page.index('  let SIGNALS =')
        end = page.index('  function repoRow', start)
        script = page[start:end]
        checks = r'''
const assert = require('node:assert/strict');
const now = Date.parse('2026-10-03T00:00:00Z');
const repos = {'EricSpencer00/work': {d90u: 9, d14u: 3}};
const repo = {full_name: 'EricSpencer00/work', stargazers_count: 7};
for (const generated of ['2026-08-19T23:36:18Z', undefined, 'invalid', '2026-10-04T00:00:00Z']) {
  SIGNALS = freshSignals({generated, repos}, now);
  assert.equal(signalFor(repo), '&#9733; 7');
}
for (const age of [0, 48 * 60 * 60 * 1000]) {
  SIGNALS = freshSignals({generated: new Date(now - age).toISOString(), repos}, now);
  assert.match(signalFor(repo), /3 this fortnight/);
}
assert.deepEqual(freshSignals({generated: '2026-10-03T00:00:00Z', repos: []}, now), {});
assert.deepEqual(freshSignals(null, now), {});
SIGNALS = freshSignals({generated: new Date(now - 48 * 60 * 60 * 1000 - 1).toISOString(), repos}, now);
assert.equal(signalFor(repo), '&#9733; 7');
assert.equal(signalFor({...repo, stargazers_count: 0}), '');
'''
        subprocess.run(['node', '-e', script + checks], check=True, capture_output=True, text=True)
