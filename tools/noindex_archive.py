#!/usr/bin/env python3
"""Keep all archived HTML out of search, including copied static pages.

Run after Hugo: python3 tools/noindex_archive.py public
Do not disallow this archive in robots.txt: crawlers need to read noindex.
"""
import re
import sys
from pathlib import Path
from html.parser import HTMLParser


class RobotsTag(HTMLParser):
    found = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and attrs.get('name', '').lower() in ('robots', 'googlebot'):
            self.found = True


def clean_meta(match):
    parser = RobotsTag()
    parser.feed(match.group())
    return '' if parser.found else match.group()


def apply(root):
    count = 0
    for path in sorted(root.rglob('*.html')):
        text = path.read_text(encoding='utf-8')
        # HTML fragments are assets, not standalone documents.
        if not re.search(r'<head(?:\s[^>]*)?>', text, re.I):
            continue
        text = re.sub(r'<meta\b[^>]*>', clean_meta, text, flags=re.I)
        text = re.sub(r'(<head(?:\s[^>]*)?>)',
                      r'\1<meta name="robots" content="noindex, follow">',
                      text, count=1, flags=re.I)
        path.write_text(text, encoding='utf-8')
        count += 1
    if not count:
        raise SystemExit('No HTML documents found; refusing an empty archive build')
    print(f'Applied noindex to {count} archived HTML documents')


if __name__ == '__main__':
    apply(Path(sys.argv[1]))
