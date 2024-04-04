from django.test.testcases import TestCase
import re


class TextRegexTests(TestCase):
    """
    Tests to see if the regex patterns actually work the way that I think they do.
    """

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

        output = list(re.finditer(pattern, test_string))

        expected_patterns = ['[[[Spring]]]', '[[[Java]]]']
        found_patterns = [x.group(0) for x in output]
        self.assertEqual(found_patterns, expected_patterns)

        expected_hyperlink_text = ['Spring', 'Java']
        found_hyperlink_text = [x.group(1) for x in output]
        self.assertEqual(found_hyperlink_text, expected_hyperlink_text)

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

        output = list(re.finditer(pattern, test_string))
        output_results = output[0]

        results_with_brackets = output_results.group(0)
        self.assertEqual(results_with_brackets, '[[[ Spring|Spring Framework ]]]')

        results_without_brackets = output_results.group(1)
        self.assertEqual(results_without_brackets, ' Spring|Spring Framework ')

        self.assertEqual(results_without_brackets.strip(), 'Spring|Spring Framework')

        split_results = results_without_brackets.split('|')
        self.assertEqual(split_results, [' Spring', 'Spring Framework '])


    def test_parsing_java_code(self):
        test_string = ' some text[java[[@Autowired public NBIServiceImpl nbiServicePort;]]] some text'
        pattern = r'\[java\[\[(.*?)\]\]\]'
        output = re.finditer(pattern, test_string)
        for x in output:
            self.assertEqual(x.group(), '[java[[@Autowired public NBIServiceImpl nbiServicePort;]]]')
            self.assertEqual(x.group(1).strip(), '@Autowired public NBIServiceImpl nbiServicePort;')

    def test_parsing_multiline_java_code(self):
        test_string = """public NBIServiceImpl nbiServicePort;</code></pre>[java[[@Autowired
                public NBIServiceImpl nbiServicePort;]]]"""
        pattern = re.compile(r'\[java\[\[(.*?)\]\]\]', re.DOTALL)
        output = re.finditer(pattern, test_string)
        for x in output:
            self.assertEqual(x.group(), '''[java[[@Autowired
                public NBIServiceImpl nbiServicePort;]]]''')
            self.assertEqual(x.group(1).strip(), '''@Autowired
                public NBIServiceImpl nbiServicePort;''')
