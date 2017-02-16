import os
from lxml import etree
from collections import defaultdict
from django.test import TestCase
from selenium import webdriver


class SeleniumTests(TestCase):

    def test_selenium(self):

        chromedriver = r'C:/Users/default.default-PC/Downloads/chromedriver.exe'
        os.environ["webdriver.chrome.driver"] = chromedriver
        driver = webdriver.Chrome(chromedriver)
        driver.get("http://www.python.org")
        assert 'Python' in driver.title
        driver.quit()


class XMLTests(TestCase):

    def test_recursive(self):

        def get_xml_file():
            module_dir = os.path.dirname(__file__)  # Gets the current path.
            file_path = os.path.join(module_dir, 'general.xml')  # This is so we can open general.xml in the current path.
            data = etree.parse(file_path)  # Creates a tree structure from general.xml.
            root_dict = etree_to_dict(data.getroot())  # Converts the tree structure into a dictionary.
            return root_dict

        def etree_to_dict(t):
            d = {t.tag: {} if t.attrib else None}
            children = list(t)
            if children:
                dd = defaultdict(list)
                for dc in map(etree_to_dict, children):
                    for k, v in dc.items():
                        dd[k].append(v)
                d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
            if t.attrib:
                d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
            if t.text:
                text = t.text.strip()
                if children or t.attrib:
                    if text:
                        d[t.tag]['#text'] = text
                else:
                    d[t.tag] = text
            return d

        def dict_recursion(input_dict):
            if type(input_dict) is dict:
                #print('input_dict is a dictionary:')
                #print(input_dict.keys())
                for dict_item in input_dict.items():
                    dict_recursion(dict_item[1])
            elif type(input_dict) is list:
                #print('input_dict is a list:')
                for x in input_dict:
                    #print('list item:')
                    #print(x)
                    dict_recursion(x)
            else:
                print('input_dict is not a dictionary:')
                print(input_dict)

        xml_dict = get_xml_file()
        dict_recursion(xml_dict)
