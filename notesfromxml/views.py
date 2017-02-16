from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from lxml import etree
from collections import defaultdict

from django.template import loader
from django.core import serializers
import os


def index(request):
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'general.xml')
    data = etree.parse(file_path)
    d = etree_to_dict(data.getroot())
    for note in d.items():
        print(note[1].keys())
    return render(request, 'notesfromxml/index.html', {'notes': d})


def xml_detail(request, detail):
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'general.xml')
    data = etree.parse(file_path)
    note_dict = etree_to_dict(data.getroot())
    detail_dict = note_dict['data'][detail]
    return render(request, 'notesfromxml/xml-category.html', {'notes': detail_dict})


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
