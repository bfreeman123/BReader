from __future__ import absolute_import, division, unicode_literals

import io

from . import support  # flake8: noqa
from html5lib import html5parser
from html5lib.constants import namespaces
from html5lib import treebuilders

import unittest

# tests that aren't autogenerated from text files


class MoreParserTests(unittest.TestCase):

    def setUp(self):
        self.dom_tree = treebuilders.getTreeBuilder("dom")

    def test_assertDoctypeCloneable(self):
        parser = html5parser.HTMLParser(tree=self.dom_tree)
        doc = parser.parse('<!DOCTYPE HTML>')
        self.assertTrue(doc.cloneNode(True))

    def test_line_counter(self):
        # http://groups.google.com/group/html5lib-discuss/browse_frm/thread/f4f00e4a2f26d5c0
        parser = html5parser.HTMLParser(tree=self.dom_tree)
        parser.parse("<pre>\nx\n&gt;\n</pre>")

    def test_namespace_html_elements_0_dom(self):
        parser = html5parser.HTMLParser(tree=self.dom_tree, namespaceHTMLElements=True)
        doc = parser.parse("<html></html>")
        self.assertTrue(doc.childNodes[0].namespaceURI == namespaces["html"])

    def test_namespace_html_elements_1_dom(self):
        parser = html5parser.HTMLParser(tree=self.dom_tree, namespaceHTMLElements=False)
        doc = parser.parse("<html></html>")
        self.assertTrue(doc.childNodes[0].namespaceURI is None)

    def test_namespace_html_elements_0_etree(self):
        parser = html5parser.HTMLParser(namespaceHTMLElements=True)
        doc = parser.parse("<html></html>")
        self.assertTrue(doc.tag == "{%s}html" % (namespaces["html"],))

    def test_namespace_html_elements_1_etree(self):
        parser = html5parser.HTMLParser(namespaceHTMLElements=False)
        doc = parser.parse("<html></html>")
        self.assertTrue(doc.tag == "html")

    def test_unicode_file(self):
        parser = html5parser.HTMLParser()
        parser.parse(io.StringIO("a"))


def buildTestSuite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)


def main():
    buildTestSuite()
    unittest.main()

if __name__ == '__main__':
    main()