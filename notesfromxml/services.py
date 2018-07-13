from .models import Tag, Document, Tagmap
import re


def handle_new_tag(new_tags, new_doc=None):
    # TODO: Update documentation for multi tag support.
    """
    Function for handling the creation of new tags, adding them to the document and saving them in the database.
    :param new_tag: A tag that is to be added to a document. The tag may already be in the database but not yet associated
    with the document that we want to link it to.
    :param new_doc: If we are creating a new document at the same time we are creating a new tag, we need to create a new
    tagmap as well.
    :return: nothing.
    """

    # Tags are separated by a comma (,) but if there is a comma in the tag name then it can be escaped with this trick.
    new_tags = new_tags.replace('\,', 'replacecommahackfromhell')
    split_tags = new_tags.split(',')
    for new_tag in split_tags:
        new_tag = new_tag.replace('replacecommahackfromhell', ',').strip()
        if Tag.objects.filter(tag_name=new_tag).exists():  # If the tag already exists.
            current_tag = Tag.objects.get(tag_name=new_tag)
        else:  # Create the new tag and save it in the database.
            current_tag = Tag(tag_name=new_tag)
            current_tag.save()
        if new_doc:  # If we are adding a tag to a newly created document.
            # If the tagmap for the newly created document and the tag does not exist.
            if not Tagmap.objects.filter(tag=current_tag, document=new_doc).exists():
                new_tagmap = Tagmap(document=new_doc, tag=current_tag)
                new_tagmap.save()


def delete_object(obj_name, obj_type, request):
    if obj_type == 'tag':  # If we are deleting a tag.
        tag_to_delete = Tag.objects.get(tag_name=obj_name)
        for tagmap in tag_to_delete.tagmap_set.all():
            tagmap.delete()
        tag_to_delete.delete()
        # if 'currently_viewed_doc' in request.POST:
        #    document = Document.objects.get(document_name=request.POST['currently_viewed_doc'])
    elif obj_type == 'document':  # If we are deleting a document.
        doc_to_delete = Document.objects.get(document_name=obj_name)
        for tagmap in doc_to_delete.tagmap_set.all():
            tagmap.delete()
        doc_to_delete.delete()


def remove_object(obj_name, obj_type, request):
    if obj_type == 'tag':
        tag_to_remove = Tag.objects.get(tag_name=obj_name)
        document = Document.objects.get(document_name=request.POST['currently_viewed_doc'])
        tagmap_to_delete = tag_to_remove.tagmap_set.get(tag=tag_to_remove, document=document)
        tagmap_to_delete.delete()
    elif obj_type == 'document':
        doc_to_remove = Document.objects.get(document_name=obj_name)
        current_tag = Tag.objects.get(tag_name=request.POST['currently_viewed_tag'])
        tagmap_to_delete = doc_to_remove.tagmap_set.get(tag=current_tag, document=doc_to_remove)
        tagmap_to_delete.delete()


def parser(parsed_text):
    parsed_text = hyperlink_parser(parsed_text)
    parsed_text = java_code_parser(parsed_text)
    return parsed_text


def hyperlink_parser(parsed_text):
    pattern = r'\[\[\[(.*?)\]\]\]'

    matches = re.finditer(pattern, parsed_text)
    if matches is not None:
        for match in matches:
            print(match)
            output_with_brackets = match.group()
            output_without_brackets = re.search(pattern, parsed_text).group(1).strip()
            if '|' in output_without_brackets:
                split_output = output_without_brackets.split('|')
                first_part = split_output[0].strip()
                second_part = split_output[1].strip()
                output_with_link = '<a href="/notesfromxml/displaydoc/' + first_part \
                                   + '">' + second_part + '</a>'
            else:
                output_with_link = '<a href="/notesfromxml/displaydoc/' + output_without_brackets \
                                   + '">' + output_without_brackets + '</a>'

            parsed_text = parsed_text.replace(output_with_brackets, output_with_link)

    return parsed_text


def java_code_parser(parsed_text):
    print('in java code parser')
    pattern = re.compile(r'\[java\[\[(.*?)\]\]\]', re.DOTALL)
    matches = re.finditer(pattern, parsed_text)
    if matches is not None:
        for match in matches:
            print(match)
            output_with_brackets = match.group()
            output_without_brackets = re.search(pattern, parsed_text).group(1).strip()
            output_with_html = '<pre><code class="language-java" data-lang="java">' + output_without_brackets \
                               + '"</code></pre>'
            parsed_text = parsed_text.replace(output_with_brackets, output_with_html)
    return parsed_text
