from django.test.testcases import TestCase
from django.test import override_settings
import re
from notes.models import Document, Tag, Tagmap
from notes.forms import AddTagForm


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

    def test_single_hyperlink_with_delimiter(self):
        test_string = 'This is where a [[[ Spring|Spring Framework ]]] hyperlink should come.'
        pattern = r'\[\[\[(.*?)\]\]\]'

        output = re.finditer(pattern, test_string)
        for x in output:
            result_without_brackets = x.group(1)
            if '|' in result_without_brackets:
                print(result_without_brackets.split('|'))
            print(x.group())

    def test_parsing_java_code(self):
        test_string = ' some text[java[[@Autowired public NBIServiceImpl nbiServicePort;]]] some text'
        pattern = r'\[java\[\[(.*?)\]\]\]'
        output = re.finditer(pattern, test_string)
        print(output)
        for x in output:
            print(x.group(1))
            self.assertEqual(x.group(), '[java[[@Autowired public NBIServiceImpl nbiServicePort;]]]')
            self.assertEqual(x.group(1).strip(), '@Autowired public NBIServiceImpl nbiServicePort;')

    def test_parsing_multiline_java_code(self):
        test_string = """public NBIServiceImpl nbiServicePort;</code></pre>[java[[@Autowired
                public NBIServiceImpl nbiServicePort;]]]"""
        pattern = re.compile(r'\[java\[\[(.*?)\]\]\]', re.DOTALL)
        output = re.finditer(pattern, test_string)
        for x in output:
            print(x.group(1))
            self.assertEqual(x.group(), '''[java[[@Autowired
                public NBIServiceImpl nbiServicePort;]]]''')
            self.assertEqual(x.group(1).strip(), '''@Autowired
                public NBIServiceImpl nbiServicePort;''')
