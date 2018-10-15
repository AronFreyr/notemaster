from notesfromxml.models import Document, Tag, Tagmap
import math
import turtle
from random import randint


def draw_document_map():
    test_tag = Tag.objects.get(tag_name='Ancient Rome')
    my_turtle = turtle.Turtle()
    my_turtle.speed(0)
    print(my_turtle.pos())
    my_turtle.color('red', 'yellow')
    docs_and_pos = {}
    my_turtle.getscreen().screensize(3000, 3000)
    #draw_recursive(my_turtle, docs_and_pos, {}, test_doc)
    draw_recursive2(my_turtle, docs_and_pos, {}, test_tag)
    turtle.done()


def draw_recursive(my_turtle, docs_and_pos, tags_and_pos, doc):
    print('doc: ' + doc.document_name)
    for tag in doc.get_all_tags():
        # print(tag.tagmap_set.all())
        if tag.tag_name not in tags_and_pos:
            offset = (randint(-100, 100), randint(-25, 25))
            my_turtle.forward(300 + offset[0])
            my_turtle.left(50 + offset[1])
            tags_and_pos[tag.tag_name] = {'x': my_turtle.pos()[0], 'y': my_turtle.pos()[1]}
            my_turtle.write('tag: ' + tag.tag_name)

        if tag.tagmap_set.all() is not None and tag.tag_name != 'Programming':
            for tagmap in tag.tagmap_set.all():
                doc_name = tagmap.document.document_name
                if doc_name in docs_and_pos.keys():
                    #my_turtle.penup()
                    my_turtle.setpos(docs_and_pos[doc_name]['x'], docs_and_pos[doc_name]['y'])
                    #my_turtle.pendown()
                else:
                    my_turtle.setpos(tags_and_pos[tag.tag_name]['x'], tags_and_pos[tag.tag_name]['y'])
                    offset = (randint(-100, 100), randint(-25, 25))
                    my_turtle.forward(300 + offset[0])
                    my_turtle.left(50 + offset[1])
                    docs_and_pos[doc_name] = {'x': my_turtle.pos()[0], 'y': my_turtle.pos()[1]}
                    my_turtle.write(doc_name)
                    draw_recursive(my_turtle, docs_and_pos, tags_and_pos, Document.objects.get(document_name=doc_name))

                    # offset = (offset[0] + 10, offset[1] + 20)


def draw_recursive2(my_turtle, docs_and_pos, tags_and_pos, tag):

    if tag.tag_name not in tags_and_pos:
        # offset = [randint(-100, 100), randint(-25, 25), randint(-25, 25)]
        new_pos = get_turtle_pos(my_turtle.pos()[0], my_turtle.pos()[1], tags_and_pos)
        my_turtle.penup()
        # my_turtle.forward(300 + offset[0])
        # my_turtle.left(50 + offset[1])
        my_turtle.setpos(new_pos[0], new_pos[1])
        my_turtle.left(50 + randint(-25, 25))

        #my_turtle.right(50 - offset[2])
        my_turtle.pendown()
        tags_and_pos[tag.tag_name] = {'x': my_turtle.pos()[0], 'y': my_turtle.pos()[1]}
        my_turtle.write('tag: ' + tag.tag_name)

        docs_to_recurse = []

        if tag.tagmap_set.all() is not None and tag.tag_name not in ['History', 'Rome']:
            for tagmap in tag.tagmap_set.all():
                doc = tagmap.document
                docs_to_recurse.append(doc)
                doc_name = doc.document_name
                if doc_name in docs_and_pos.keys():
                    my_turtle.setpos(docs_and_pos[doc_name]['x'], docs_and_pos[doc_name]['y'])
                else:
                    my_turtle.setpos(tags_and_pos[tag.tag_name]['x'], tags_and_pos[tag.tag_name]['y'])
                    # new_pos2 = get_turtle_pos(my_turtle.pos()[0], my_turtle.pos()[1], docs_and_pos)
                    offset = [randint(-100, 100), randint(-25, 25), randint(-25, 25)]
                    my_turtle.forward(300 + offset[0])
                    my_turtle.left(50 + offset[1])
                    # my_turtle.setpos(new_pos2[0], new_pos2[1])
                    # my_turtle.left(50 + randint(-25, 25))
                    #my_turtle.right(50 - offset[2])
                    docs_and_pos[doc_name] = {'x': my_turtle.pos()[0], 'y': my_turtle.pos()[1]}
                    my_turtle.write(doc_name)

                my_turtle.penup()
                my_turtle.setpos(tags_and_pos[tag.tag_name]['x'], tags_and_pos[tag.tag_name]['y'])
                my_turtle.pendown()

            for recurse_doc in docs_to_recurse:
                for new_tag in recurse_doc.get_all_tags():
                    if new_tag.tag_name != tag.tag_name:
                        draw_recursive2(my_turtle, docs_and_pos, tags_and_pos, new_tag)

                    # offset = (offset[0] + 10, offset[1] + 20)
    else:
        return


def get_turtle_pos(old_x, old_y, tags_and_pos):
    test_turtle = turtle.Turtle()
    test_turtle.speed(0)
    test_turtle.penup()
    test_turtle.setpos(old_x, old_y)
    while True:
        offset = [randint(-100, 100), randint(-25, 25), randint(-25, 25)]
        test_turtle.left(100 + offset[1])
        test_turtle.forward(300 + offset[0])

        for tag_key in tags_and_pos.keys():
            new_x = test_turtle.pos()[0]
            new_y = test_turtle.pos()[1]
            #print('new_x=' + str(new_x) + ' - new_y=' + str(new_y))
            tag_x = tags_and_pos[tag_key]['x']
            tag_y = tags_and_pos[tag_key]['y']
            #print('tag_x=' + str(tag_x) + ' - tag_y=' + str(tag_y))
            if math.isclose(tag_x, new_x, rel_tol=0.05):
                if math.isclose(tag_y, new_y, rel_tol=0.05):
                    break
            if not is_pos_within_frame(new_x, new_y):
                break
        else:
            return_pos = test_turtle.pos()
            test_turtle.reset()
            return return_pos


def is_pos_within_frame(x, y):
    if 1000 > x > -1000:
        if 1000 > y > -1000:
            return True
    return False
