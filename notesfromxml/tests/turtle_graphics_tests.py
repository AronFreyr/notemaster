from notesfromxml.models import Document, Tag, Tagmap
import turtle
from random import randint


def draw_document_map():

    test_doc = Document.objects.get(document_name='Spring')
    test_doc2 = Document.objects.get(document_name='Spring Annotations')
    doc_list = [test_doc, test_doc2]
    my_turtle = turtle.Turtle()
    my_screen = turtle.Screen()
    #my_screen.screensize(2000, 2000)
    my_turtle.color('red', 'yellow')
    docs_and_pos = {}
    offset = (10, 20)
    my_turtle.getscreen().screensize(3000, 3000)
    for doc in doc_list:
        draw_recursive(my_turtle, docs_and_pos, doc)
        """"#for tag in doc.get_all_tags():
            # print(tag.tagmap_set.all())
            if tag.tagmap_set.all() is not None and tag.tag_name != 'Programming':
                for tagmap in tag.tagmap_set.all():
                    doc_name = tagmap.document.document_name
                    if doc_name in docs_and_pos.keys():
                        my_turtle.penup()
                        my_turtle.setpos(docs_and_pos[doc_name]['x'], docs_and_pos[doc_name]['y'])
                        my_turtle.pendown()
                    else:
                        my_turtle.forward(200 + offset[0])
                        my_turtle.left(50 + offset[1])
                        docs_and_pos[doc_name] = {'x': my_turtle.pos()[0], 'y': my_turtle.pos()[1]}
                        my_turtle.write(doc_name)

                        #offset = (offset[0] + 10, offset[1] + 20)
                        offset = (randint(-50, 50), randint(-25, 25))
                    print(docs_and_pos)"""
                # my_turtle.write(tag.tag_name)
                # my_turtle.forward(200)
                # my_turtle.left(100)
    turtle.done()


def draw_recursive(my_turtle, docs_and_pos, doc):
    offset = (10, 20)
    print('doc: ' + doc.document_name)
    for tag in doc.get_all_tags():
        # print(tag.tagmap_set.all())
        if tag.tagmap_set.all() is not None and tag.tag_name != 'Programming':
            for tagmap in tag.tagmap_set.all():
                doc_name = tagmap.document.document_name
                if doc_name in docs_and_pos.keys():
                    #my_turtle.penup()
                    my_turtle.setpos(docs_and_pos[doc_name]['x'], docs_and_pos[doc_name]['y'])
                    #my_turtle.pendown()
                else:
                    offset = (randint(-100, 100), randint(-25, 25))
                    my_turtle.forward(300 + offset[0])
                    my_turtle.left(50 + offset[1])
                    docs_and_pos[doc_name] = {'x': my_turtle.pos()[0], 'y': my_turtle.pos()[1]}
                    my_turtle.write(doc_name)
                    draw_recursive(my_turtle, docs_and_pos, Document.objects.get(document_name=doc_name))

                    # offset = (offset[0] + 10, offset[1] + 20)
