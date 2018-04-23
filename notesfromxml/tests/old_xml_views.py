from lxml import etree
from collections import defaultdict
import os
from django.shortcuts import render


# Old XML views that I wasn't ready to throw away but didn't know where to store them.

def xml_detail(request, detail):
    root_dict = get_xml_file()
    detail_dict = root_dict['data'][detail]
    return render(request, 'notesfromxml/old_xml_templates/xml-category.html', {'notes': detail_dict})


# Technically this function can only get a single xml file: 'general.xml'.
def get_xml_file():
    """
    Gets the 'general.xml' file in the current directory and converts it to a Python dictionary.
    :return: the root of a Python dictionary that represents the data in an xml file.
    """
    module_dir = os.path.dirname(__file__)  # Gets the current path.
    file_path = os.path.join(module_dir, 'tests/general.xml')  # This is so we can open general.xml in the current path.
    data = etree.parse(file_path)  # Creates a tree structure from general.xml.
    root_dict = etree_to_dict(data.getroot())  # Converts the tree structure into a dictionary.
    return root_dict


# This function was acquired from the internet.
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
