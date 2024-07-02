from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import markdown

from notes.models import Document, Tag, Tagmap, Image, ImageDocumentMap, ImageTagMap

# A test function to create a test homepage.
@login_required
def display_homepage_test(request):

    latest_programming_documents = Document.objects.filter(tagmap__tag__tag_name='Programming').order_by('-id')[:5]
    latest_history_documents = Document.objects.filter(tagmap__tag__tag_name='History').order_by('-id')[:5]

    return render(request, 'notes/homepage-test.html',
                  {'latest_programming_docs': latest_programming_documents,
                   'latest_history_docs': latest_history_documents})

# A test view that displays the stuff behind the "Test" button in the navigation bar.
@login_required
def display_tests(request):
    #test_create_xml_from_documents()
    #test_create_graph()
    messages.add_message(request, messages.INFO, 'test message')
    md = markdown.markdown('$ \sqrt{37}$')
    #md = markdown.markdown('tesxt in the text._Italics_. **Bold**. $$e^x$$',
    #                       extensions=['mdx_math'])
    #md = markdown.Markdown(extensions=['mdx_math'], extension_configs={
    #    'mdx-math': {'enable_dollar_delimiter': True}})
    #md = md.convert('$$e^x$$')
  #                         extensions=['markdown.extensions.fenced_code', 'mdx_math'])
    return render(request, 'notes/tests.html', {'markdown': md})
