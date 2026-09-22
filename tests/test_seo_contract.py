"""Regression checks for analytics policies and discoverable canonical pages."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_site import PageParser, check_analytics, check_discovery
from seo_tags import CSP
from apply_ga4 import TAG


def page(html):
    parser = PageParser()
    parser.feed(html)
    return parser


class SEOContractTests(unittest.TestCase):
    def test_deployed_analytics_tag_can_load_and_collect(self):
        self.assertEqual(check_analytics(page(CSP + TAG)), [])

    def test_old_policy_catches_loader_and_collection_regression(self):
        old = '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; script-src \'self\' https://esm.run; connect-src \'self\' https://api.github.com">'
        problems = check_analytics(page(old + TAG))
        self.assertTrue(any('loader' in p for p in problems))
        self.assertTrue(any('collection' in p for p in problems))

    def test_more_specific_script_policy_cannot_be_bypassed(self):
        blocked = CSP.replace("script-src 'self'", "script-src-elem 'self'; script-src 'self'")
        self.assertTrue(any('loader' in p for p in check_analytics(page(blocked + TAG))))

    def test_each_policy_must_allow_analytics(self):
        blocked = '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'">'
        self.assertTrue(check_analytics(page(CSP + blocked + TAG)))

    def test_external_repository_is_not_an_internal_writeup_link(self):
        pages = {
            'https://ericspencer.us/': page('<a href="https://github.com/EricSpencer00/ai-os">AuraOS</a>'),
            'https://ericspencer.us/projects/ai-os/': page('<a href="/">Home</a>'),
        }
        self.assertEqual(len(check_discovery(pages)), 1)
        pages['https://ericspencer.us/'] = page('<a href="/projects/ai-os/#status">AuraOS writeup</a>')
        self.assertEqual(check_discovery(pages), [])

    def test_self_link_does_not_make_a_page_discoverable(self):
        pages = {'https://ericspencer.us/': page(''),
                 'https://ericspencer.us/projects/ai-os/': page('<a href="#top">Top</a>')}
        self.assertEqual(len(check_discovery(pages)), 1)


if __name__ == '__main__':
    unittest.main()
