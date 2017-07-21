from django.test import TestCase
from posts.forms import markup


class MarkupTest(TestCase):
    """ Check narkup for single tag"""
    def test_single_bold_text(self):
        text = "**bold**"
        expection = "<strong>bold</strong>"
        self.assertEqual(markup(text, 'text'), expection)

    def test_single_italic_text(self):
        text = "*italic*"
        expection = "<em>italic</em>"
        self.assertEqual(markup(text, 'text'), expection)

    def test_single_spoiler_text(self):
        text = "%%spoiler%%"
        expection = '<span class="spoiler">spoiler</span>'
        self.assertEqual(markup(text, 'text'), expection)

    def test_single_strike_text(self):
        text = "~~strike~~"
        expection = "<strike>strike</strike>"
        self.assertEqual(markup(text, 'text'), expection)

    def test_single_underline_text(self):
        text = "__underline__"
        expection = "<u>underline</u>"
        self.assertEqual(markup(text, 'text'), expection)

    """ Check narkup for single tag"""
    def test_double_bold_text(self):
        text = "**first bold** **second bold**"
        expection = "<strong>first bold</strong> <strong>second bold</strong>"
        self.assertEqual(markup(text, 'text'), expection)

    def test_double_italic_text(self):
        text = "*first italic* *second italic*"
        expection = "<em>first italic</em> <em>second italic</em>"
        self.assertEqual(markup(text, 'text'), expection)

    def test_double_spoiler_text(self):
        text = "%%first spoiler%% %%second spoiler%%"
        expection = '<span class="spoiler">first spoiler</span> '\
            + '<span class="spoiler">second spoiler</span>'
        self.assertEqual(markup(text, 'text'), expection)

    def test_double_strike_text(self):
        text = "~~first strike~~ ~~second strike~~"
        expection = "<strike>first strike</strike> "\
            + "<strike>second strike</strike>"
        self.assertEqual(markup(text, 'text'), expection)

    def test_double_underline_text(self):
        text = "__first underline__ __second underline__"
        expection = "<u>first underline</u> <u>second underline</u>"
        self.assertEqual(markup(text, 'text'), expection)
