import os
from lxml import etree
from collections import defaultdict
from django.test.testcases import TestCase
from notesfromxml.models import Document, Tag, Tagmap
import urllib.request


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
                    #print('dict item[0]', dict_item[0])
                    dict_recursion(dict_item[1])
            elif type(input_dict) is list:
                #print('input_dict is a list:')
                for x in input_dict:
                    #print('list item:')
                    #print(x)
                    dict_recursion(x)
            #else:
                #print('input_dict is not a dictionary:')
                #print(input_dict)

        xml_dict = get_xml_file()
        dict_recursion(xml_dict)
        html_string = ''

        def dict_recursion_with_html(input_dict, html_string_input):
            if input_dict is None:
                print('input_dict is None')
                return
            print('input_dict', input_dict)
            if type(input_dict) is dict:
                print('input_dict is a dictionary:')
                #print(input_dict.keys())
                for dict_item in input_dict.items():
                    print('<div>')
                    html_string_input += '<h2>' + dict_item[0] + '</h2>'
                    print('dict item[0]', '<h2>' + dict_item[0] + '</h2>')
                    dict_recursion_with_html(dict_item[1], html_string_input)
                    print('</div>')
            elif type(input_dict) is list:
                print('input_dict is a list:')
                for x in input_dict:
                    #print('list item:')
                    #print(x)
                    dict_recursion_with_html(x, html_string_input)
            else:
                #print('input_dict is not a dictionary:')
                print('<p>' + input_dict + '</p>')
                html_string_input += '<p>' + input_dict + '</p>'
            print('html_string_input: ', html_string_input)
            print('END!!!')

        dict_recursion_with_html(xml_dict, html_string)
         #return_html = dict_recursion_with_html(xml_dict, html_string)


# Not working. I need to be signed in to dropbox for this to work.
class DropboxTests(TestCase):
    def test_download_from_dropbox(self):
        url = 'https://www.dropbox.com/home/glosur/general.xml?dl=1'
        #url = 'https://dl.dropboxusercontent.com/content_link/moluVccftJLq0UwJkGW3QFZri4OgGPgOzNa7d913SSnnwgoHKFbPYhKCnUhuffgQ/file'
        u = urllib.request.urlopen(url)
        data = u.read()
        u.close()
        print(data)


class DatabaseTests(TestCase):

    def test_data_relations(self):
        Document.objects.create(document_name="Java", document_text="Java document text test 1")
        Document.objects.create(document_name="JAXB", document_text="JAXB document text test 1")
        Document.objects.create(document_name="XML", document_text="XML document text test 1")

        Tag.objects.create(tag_name="Java")
        Tag.objects.create(tag_name="JAXB")
        Tag.objects.create(tag_name="XML")

        Tagmap.objects.create(document=Document.objects.get(document_name="Java"), tag=Tag.objects.get(tag_name="Java"))
        Tagmap.objects.create(document=Document.objects.get(document_name="JAXB"), tag=Tag.objects.get(tag_name="Java"))
        Tagmap.objects.create(document=Document.objects.get(document_name="JAXB"), tag=Tag.objects.get(tag_name="JAXB"))
        Tagmap.objects.create(document=Document.objects.get(document_name="JAXB"), tag=Tag.objects.get(tag_name="XML"))
        Tagmap.objects.create(document=Document.objects.get(document_name="XML"), tag=Tag.objects.get(tag_name="XML"))

        java_doc = Document.objects.get(document_name='Java')

        for tagmap in java_doc.tagmap_set.all():
            print(tagmap.tag.tag_name)
            for tag in tagmap.tag.tagmap_set.all():
                print(tag.document.document_name)
