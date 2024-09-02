from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from lxml import etree as LET
from lxml import objectify
from notes.models import Document, Tag, Tagmap, Image, ImageDocumentMap, ImageTagMap
from taskmaster.models import Task, TaskBoard, TaskList
from timemaster.models import Activity, TimeInterval


def index(request):
    pass


@login_required
def documents(request):
    return HttpResponse(create_xml_from_documents(), content_type='text/xml')

@login_required
def tags(request):
    return HttpResponse(create_xml_from_tags(), content_type='text/xml')

@login_required
def tasks(request):
    return HttpResponse(create_xml_from_tasks(), content_type='text/xml')

@login_required
def task_lists(request):
    return HttpResponse(create_xml_from_task_lists(), content_type='text/xml')

@login_required
def task_boards(request):
    return HttpResponse(create_xml_from_task_boards(), content_type='text/xml')

@login_required
def activities(request):
    return HttpResponse(create_xml_from_activities(), content_type='text/xml')

@login_required
def time_intervals(request):
    return HttpResponse(create_xml_from_time_intervals(), content_type='text/xml')


def create_xml_from_documents():
    all_docs = Document.objects.all()

    xml_text = '<documents>\n'
    for doc in all_docs:
        xml_text += '<document>\n'
        xml_text += '<document_id>' + str(doc.id) + '</document_id>\n'
        xml_text += '<name>' + doc.document_name + '</name>\n'
        input_text = doc.document_text
        while ']]>' in input_text:
            input_text = input_text.replace(']]>', '.\].\].\>')
        while '<![CDATA[' in input_text:
            input_text = input_text.replace('<![CDATA[', '\<!\[CDATA\[')
        xml_text += '<text> <![CDATA[' + input_text + ']]> </text>\n'
        xml_text += '<document_tags>\n'
        for tag in doc.get_all_tags_sorted():
            xml_text += '<document_tag>\n'
            xml_text += '<tag_id>' + str(tag.id) + '</tag_id>\n'
            xml_text += '<tag_name>' + tag.tag_name + '</tag_name>\n'
            xml_text += '<tag_type>' + tag.tag_type + '</tag_type>\n'
            xml_text += '<meta_tag_type>' + tag.meta_tag_type + '</meta_tag_type>\n'
            xml_text += '</document_tag>\n'
        xml_text += '</document_tags>\n'
        xml_text += '<last_modified>' + doc.document_modified.strftime('%Y-%m-%d') + '</last_modified> \n'
        xml_text += '<last_modified_by>' + str(doc.document_last_modified_by) + '</last_modified_by> \n'
        xml_text += '<created>' + doc.document_created.strftime('%Y-%m-%d') + '</created> \n'
        xml_text += '<created_by>' + str(doc.document_created_by) + '</created_by> \n'
        xml_text += '<document_type>' + doc.document_type + '</document_type> \n'
        xml_text += '</document>\n'
    xml_text += '</documents>'

    xml_element = LET.ElementTree(objectify.fromstring(xml_text))

    xml_to_string = LET.tostring(xml_element.getroot(), pretty_print=True, xml_declaration=True,
                                 encoding='UTF-8').decode()

    return xml_to_string


def create_xml_from_tags():
    # Convert all of the tags in the database to XML.
    all_tags = Tag.objects.all()  # Get all of the tags.
    xml_text = '<tags>\n'
    for tag in all_tags:
        xml_text += '<tag>\n'
        xml_text += '<name>' + tag.tag_name + '</name>\n'
        xml_text += '<tag_type>' + tag.tag_type + '</tag_type>\n'
        xml_text += '<meta_tag_type>' + tag.meta_tag_type + '</meta_tag_type>\n'
        xml_text += '<tag_documents>\n'
        for document in tag.get_all_docs():  # Get all docs associated with a tag.
            xml_text += '<tag_document>\n'
            xml_text += '<document_name>' + document.document_name + '</document_name>\n'
            doc_text = document.document_text
            # XML escape.
            while ']]>' in doc_text:
                doc_text = doc_text.replace(']]>', '.\].\].\>')
            while '<![CDATA[' in doc_text:
                doc_text = doc_text.replace('<![CDATA[', '\<!\[CDATA\[')
            xml_text += '<document_text> <![CDATA[' + doc_text + ']]> </document_text>\n'
            xml_text += '<document_type>' + document.document_type + '</document_type>\n'
            xml_text += '</tag_document>\n'
        xml_text += '</tag_documents>\n'
        xml_text += '<last_modified>' + tag.tag_modified.strftime('%Y-%m-%d') + '</last_modified> \n'
        xml_text += '<last_modified_by>' + str(tag.tag_last_modified_by) + '</last_modified_by> \n'
        xml_text += '<created>' + tag.tag_created.strftime('%Y-%m-%d') + '</created> \n'
        xml_text += '<created_by>' + str(tag.tag_created_by) + '</created_by> \n'
        xml_text += '</tag>\n'
    xml_text += '</tags>'

    xml_element = LET.ElementTree(objectify.fromstring(xml_text))

    xml_to_string = LET.tostring(xml_element.getroot(), pretty_print=True, xml_declaration=True,
                                 encoding='UTF-8').decode()

    return xml_to_string


def create_xml_from_tasks():
    all_tasks = Task.objects.all()
    xml_text = '<tasks>\n'
    for task in all_tasks:
        xml_text += '<task_id>' + str(task.id) + '</task_id>\n'
        xml_text += '<task_name>' + task.document_name + '</task_name>\n'
        input_text = task.document_text
        while ']]>' in input_text:
            input_text = input_text.replace(']]>', '.\].\].\>')
        while '<![CDATA[' in input_text:
            input_text = input_text.replace('<![CDATA[', '\<!\[CDATA\[')
        xml_text += '<text> <![CDATA[' + input_text + ']]> </text>\n'
        xml_text += '<task_tags>\n'
        for tag in task.get_all_tags_sorted():
            xml_text += '<task_tag>\n'
            xml_text += '<tag_id>' + str(tag.id) + '</tag_id>\n'
            xml_text += '<tag_name>' + tag.tag_name + '</tag_name>\n'
            xml_text += '<tag_type>' + tag.tag_type + '</tag_type>\n'
            xml_text += '<meta_tag_type>' + tag.meta_tag_type + '</meta_tag_type>\n'
            xml_text += '</task_tag>\n'
        xml_text += '</task_tags>\n'
        xml_text += '<last_modified>' + task.document_modified.strftime('%Y-%m-%d') + '</last_modified> \n'
        xml_text += '<last_modified_by>' + str(task.document_last_modified_by) + '</last_modified_by> \n'
        xml_text += '<created>' + task.document_created.strftime('%Y-%m-%d') + '</created> \n'
        xml_text += '<created_by>' + str(task.document_created_by) + '</created_by> \n'
        xml_text += '<document_type>' + task.document_type + '</document_type> \n'
        xml_text += '<task_difficulty>' + str(task.task_difficulty) + '</task_difficulty> \n'
        xml_text += '<task_importance>' + str(task.task_importance) + '</task_importance> \n'
        xml_text += '<task_assigned_to>' + task.task_assigned_to + '</task_assigned_to> \n'
        if task.task_deadline:
            xml_text += '<task_deadline>' + task.task_deadline.strftime('%Y-%m-%d') + '</task_deadline> \n'
        else:
            xml_text += '<task_deadline></task_deadline> \n'
        if task.task_list:
            xml_text += '<task_list>\n'
            xml_text += '<task_list_id>' + str(task.task_list.id) + '</task_list_id>\n'
            xml_text += '<task_list_name>' + str(task.task_list.list_name) + '</task_list_name>\n'
            xml_text += '</task_list>\n'
        else:
            xml_text += '<task_list></task_list>\n'
        xml_text += '<task_board>\n'
        xml_text += '<task_board_id>' + str(task.task_board.id) + '</task_board_id>\n'
        xml_text += '<task_board_name>' + str(task.task_board.board_name) + '</task_board_name>\n'
        xml_text += '</task_board>\n'
        if task.next_task:
            xml_text += '<next_task>\n'
            xml_text += '<next_task_id>' + str(task.next_task.id) + '</next_task_id>\n'
            xml_text += '<next_task_name>' + str(task.next_task.document_name) + '</next_task_name>\n'
            xml_text += '</next_task>\n'
        else:
            xml_text += '<next_task></next_task>\n'
        if task.previous_task:
            xml_text += '<previous_task>\n'
            xml_text += '<previous_task_id>' + str(task.previous_task.id) + '</previous_task_id>\n'
            xml_text += '<previous_task_name>' + str(task.previous_task.document_name) + '</previous_task_name>\n'
            xml_text += '</previous_task>\n'
        else:
            xml_text += '<previous_task></previous_task>\n'
        if task.parent_task:
            xml_text += '<parent_task>\n'
            xml_text += '<parent_task_id>' + str(task.parent_task.id) + '</parent_task_id>\n'
            xml_text += '<parent_task_name>' + str(task.parent_task.document_name) + '</parent_task_name>\n'
            xml_text += '</parent_task>\n'
        else:
            xml_text += '<parent_task></parent_task>\n'

    xml_text += '</tasks>'

    xml_element = LET.ElementTree(objectify.fromstring(xml_text))
    xml_to_string = LET.tostring(xml_element.getroot(), pretty_print=True, xml_declaration=True,
                                 encoding='UTF-8').decode()
    return xml_to_string

def create_xml_from_task_lists():
    all_task_lists = TaskList.objects.all()
    xml_text = '<task_lists>\n'
    for task_list in all_task_lists:
        xml_text += '<task_list_id>' + str(task_list.id) + '</task_list_id>\n'
        xml_text += '<task_list_name>' + task_list.list_name + '</task_list_name>\n'

        xml_text += '<task_list_board>\n'
        xml_text += '<task_list_board_id>' + str(task_list.list_board.id) + '</task_list_board_id>\n'
        xml_text += '<task_list_board_name>' + str(task_list.list_board.board_name) + '</task_list_board_name>\n'
        xml_text += '</task_list_board>\n'

        if task_list.next_list:
            xml_text += '<next_list>\n'
            xml_text += '<next_list_id>' + str(task_list.next_list.id) + '</next_list_id>\n'
            xml_text += '<next_list_name>' + str(task_list.next_list.list_name) + '</next_list_name>\n'
            xml_text += '</next_list>\n'
        else:
            xml_text += '<next_list></next_list>\n'

        if task_list.previous_list:
            xml_text += '<previous_list>\n'
            xml_text += '<previous_list_id>' + str(task_list.previous_list.id) + '</previous_list_id>\n'
            xml_text += '<previous_list_name>' + str(task_list.previous_list.list_name) + '</previous_list_name>\n'
            xml_text += '</previous_list>\n'
        else:
            xml_text += '<previous_list></previous_list>\n'

        xml_text += '<task_list_tasks>\n'
        for task in task_list.get_all_tasks_in_list():
            xml_text += '<task>\n'
            xml_text += '<task_id>' + str(task.id) + '</task_id>\n'
            xml_text += '<task_name>' + task.document_name + '</task_name>\n'
            xml_text += '</task>\n'
        xml_text += '</task_list_tasks>\n'

    xml_text += '</task_lists>'

    xml_element = LET.ElementTree(objectify.fromstring(xml_text))
    xml_to_string = LET.tostring(xml_element.getroot(), pretty_print=True, xml_declaration=True,
                                 encoding='UTF-8').decode()
    return xml_to_string

def create_xml_from_task_boards():
    all_task_boards = TaskBoard.objects.all()
    xml_text = '<task_boards>\n'
    for task_board in all_task_boards:
        xml_text += '<task_board>\n'
        xml_text += '<task_board_id>' + str(task_board.id) + '</task_board_id>\n'
        xml_text += '<task_board_name>' + task_board.board_name + '</task_board_name>\n'
        xml_text += '<board_created>' + task_board.board_created.strftime('%Y-%m-%d') + '</board_created>\n'
        xml_text += '<board_created_by>' + str(task_board.board_created_by) + '</board_created_by>\n'
        xml_text += '<board_modified>' + task_board.board_modified.strftime('%Y-%m-%d') + '</board_modified>\n'
        xml_text += '<board_last_modified_by>' + str(task_board.board_last_modified_by) + '</board_last_modified_by>\n'

        xml_text += '<task_lists>\n'
        for task_list in task_board.get_all_lists_in_board_in_custom_order():
            xml_text += '<task_list>\n'
            xml_text += '<task_list_id>' + str(task_list.id) + '</task_list_id>\n'
            xml_text += '<task_list_name>' + task_list.list_name + '</task_list_name>\n'
            xml_text += '</task_list>'
        xml_text += '</task_lists>\n'
        xml_text += '</task_board>\n'

    xml_text += '</task_boards>'

    xml_element = LET.ElementTree(objectify.fromstring(xml_text))
    xml_to_string = LET.tostring(xml_element.getroot(), pretty_print=True, xml_declaration=True,
                                 encoding='UTF-8').decode()
    return xml_to_string


def create_xml_from_activities():
    all_activities = Activity.objects.all()

    xml_text = '<activities>\n'
    for activity in all_activities:
        xml_text += '<activity>\n'
        xml_text += '<activity_id>' + str(activity.id) + '</activity_id>\n'
        xml_text += '<name>' + activity.document_name + '</name>\n'
        input_text = activity.document_text
        while ']]>' in input_text:
            input_text = input_text.replace(']]>', '.\].\].\>')
        while '<![CDATA[' in input_text:
            input_text = input_text.replace('<![CDATA[', '\<!\[CDATA\[')
        xml_text += '<text> <![CDATA[' + input_text + ']]> </text>\n'
        xml_text += '<activity_tags>\n'
        for tag in activity.get_all_tags_sorted():
            xml_text += '<activity_tag>\n'
            xml_text += '<tag_id>' + str(tag.id) + '</tag_id>\n'
            xml_text += '<tag_name>' + tag.tag_name + '</tag_name>\n'
            xml_text += '<tag_type>' + tag.tag_type + '</tag_type>\n'
            xml_text += '<meta_tag_type>' + tag.meta_tag_type + '</meta_tag_type>\n'
            xml_text += '</activity_tag>\n'
        xml_text += '</activity_tags>\n'
        xml_text += '<last_modified>' + activity.document_modified.strftime('%Y-%m-%d') + '</last_modified> \n'
        xml_text += '<last_modified_by>' + str(activity.document_last_modified_by) + '</last_modified_by> \n'
        xml_text += '<created>' + activity.document_created.strftime('%Y-%m-%d') + '</created> \n'
        xml_text += '<created_by>' + str(activity.document_created_by) + '</created_by> \n'
        xml_text += '<document_type>' + activity.document_type + '</document_type> \n'
        xml_text += '</activity>\n'
    xml_text += '</activities>'

    xml_element = LET.ElementTree(objectify.fromstring(xml_text))

    xml_to_string = LET.tostring(xml_element.getroot(), pretty_print=True, xml_declaration=True,
                                 encoding='UTF-8').decode()

    return xml_to_string


def create_xml_from_time_intervals():
    all_time_intervals = TimeInterval.objects.all()

    xml_text = '<time_intervals>\n'

    for interval in all_time_intervals:
        xml_text += '<time_interval>\n'
        xml_text += '<time_interval_id>' + str(interval.id) + '</time_interval_id>\n'
        xml_text += '<time_interval_date>' + interval.interval_date.strftime('%Y-%m-%d') + '</time_interval_date>\n'
        xml_text += '<time_interval_amount>' + str(interval.interval_amount) + '</time_interval_amount>\n'
        xml_text += '<time_interval_tags>\n'
        for tag in interval.get_all_tags():
            xml_text += '<time_interval_tag>\n'
            xml_text += '<tag_id>' + str(tag.id) + '</tag_id>\n'
            xml_text += '<tag_name>' + tag.tag_name + '</tag_name>\n'
            xml_text += '<tag_type>' + tag.tag_type + '</tag_type>\n'
            xml_text += '<meta_tag_type>' + tag.meta_tag_type + '</meta_tag_type>\n'
            xml_text += '</time_interval_tag>\n'
        xml_text += '</time_interval_tags>\n'

        xml_text += '</time_interval>\n'

    xml_text += '</time_intervals>'

    xml_element = LET.ElementTree(objectify.fromstring(xml_text))

    xml_to_string = LET.tostring(xml_element.getroot(), pretty_print=True, xml_declaration=True,
                                 encoding='UTF-8').decode()

    return xml_to_string