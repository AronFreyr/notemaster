from django.test.testcases import TestCase
import re
from notesfromxml.models import Document, Tag, Tagmap
from notesfromxml.forms import AddTagForm


class TextFormattingTests(TestCase):

    def test_single_hyperlink(self):
        """
        Using Regex to take a string that has this: [[[some text]]]
        and extract the 'some text' out of it.
        :return:
        """
        test_string = 'This is where a [[[Spring]]] hyperlink should come.'

        pattern = r'\[\[\[(.*?)\]\]\]'

        output = re.search(pattern, test_string).group(1)

        self.assertEqual(output, 'Spring')

    def test_multiple_hyperlinks(self):

        test_string = 'This is where a [[[Spring]]] hyperlink should come, and the [[[Java]]] hyperlink.'

        pattern = r'\[\[\[(.*?)\]\]\]'

        output = re.finditer(pattern, test_string)
        for x in output:
            print(x.group())
            print(x.group(1))

    def test_single_hyperlink_with_whitespace(self):
        test_string = 'This is where a [[[ Spring ]]] hyperlink should come.'

        pattern = r'\[\[\[(.*?)\]\]\]'

        output = re.finditer(pattern, test_string)
        for x in output:
            self.assertEqual(x.group(1), ' Spring ')
            self.assertEqual(x.group(1).strip(), 'Spring')
