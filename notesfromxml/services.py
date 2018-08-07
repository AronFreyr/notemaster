from .models import Tag, Document, Tagmap, ImageTagMap, Image
import re


def handle_new_tag(new_tags, new_doc=None, new_image=None):
    # TODO: Update documentation for multi tag support and ImageTagMaps.
    # TODO: Create functionality for DocumentTagMaps.
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
        if new_image:
            if not ImageTagMap.objects.filter(tag=current_tag, image=new_image).exists():
                new_image_tagmap = ImageTagMap(image=new_image, tag=current_tag)
                new_image_tagmap.save()


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
    parsed_text = image_insert_parser(parsed_text)
    parsed_text = links_to_table_parser(parsed_text)
    return parsed_text


def hyperlink_parser(parsed_text):
    pattern = r'\[\[\[(.*?)\]\]\]'

    matches = re.finditer(pattern, parsed_text)
    if matches is not None:
        for match in set(matches):
            print(match)
            document_name = ''
            document_parameters = ''
            output_with_link = ''
            output_with_brackets = match.group()
            output_without_brackets = match.group(1)
            if '|' in output_without_brackets:
                split_output = output_without_brackets.split('|')
                document_name = split_output[0].strip()
                document_parameters = split_output[1].strip()
            else:
                document_name = output_without_brackets
                document_parameters = output_without_brackets
            if Document.objects.filter(document_name=document_name).exists():
                output_with_link = '<a href="/notesfromxml/displaydoc/' + document_name \
                                   + '">' + document_parameters + '</a>'
            else:
                output_with_link = '<a href="/notesfromxml/displaydoc/' + document_name \
                                   + '" class="broken-link">' + document_parameters + '</a>'
            parsed_text = parsed_text.replace(output_with_brackets, output_with_link)

    return parsed_text


def java_code_parser(parsed_text):
    pattern = re.compile(r'\[java\[\[(.*?)\]\]\]', re.DOTALL)
    matches = re.finditer(pattern, parsed_text)
    if matches is not None:
        for match in matches:
            print(match)
            output_with_brackets = match.group()
            # TODO: Weird to search the text again? need to test this.
            output_without_brackets = re.search(pattern, parsed_text).group(1).strip()
            output_with_html = '<pre><code class="language-java" data-lang="java">' + output_without_brackets \
                               + '</code></pre>'
            parsed_text = parsed_text.replace(output_with_brackets, output_with_html)
    return parsed_text


def image_insert_parser(parsed_text):
    pattern = re.compile(r'\[image\[\[(.*?)\]\]\]', re.DOTALL)
    matches = re.finditer(pattern, parsed_text)
    if matches is not None:
        for match in matches:
            print(match)
            image_name = ''
            style_string = ''  # String added to the HTML to apply style to the image.
            output_with_brackets = match.group()  # Example: [image[[My Image]]]
            output_without_brackets = re.search(pattern, parsed_text).group(1).strip()   # Example: My Image

            if '|' in output_without_brackets:
                split_output = output_without_brackets.split('|')
                image_name = split_output[0].strip()
                image_parameters = [x.strip() for x in split_output[1].split(',')]
                for parameter in image_parameters:
                    if 'side' in parameter:  # Which side should the image be on?
                        style_string += 'float:' + parameter.split('=')[1].strip() + ';'
                style_string = 'style="' + style_string + '"'

            else:
                image_name = output_without_brackets

            if Image.objects.filter(image_name=image_name).exists():
                image = Image.objects.get(image_name=image_name)
                output_with_html = '<img src="' + image.image_picture.url + '" alt="' \
                                   + image.image_name + '"' \
                                   + 'class="img-responsive img-rounded img-in-text"' + style_string + '>'
                parsed_text = parsed_text.replace(output_with_brackets, output_with_html)
    return parsed_text


def links_to_table_parser(parsed_text):
    pattern = re.compile(r'\[links\[\[(.*?)\]\]\]', re.DOTALL)
    matches = re.finditer(pattern, parsed_text)
    if matches is not None:
        for match in matches:
            output_with_html = '<div class="link-list"> <p class="link-list-header">Links</p> <ul>'
            print(match)
            output_with_brackets = match.group()
            output_without_brackets = re.search(pattern, parsed_text).group(1).strip()
            split_output = output_without_brackets.split(';')
            for split in split_output:
                if split is not '':  # If ; is at the end of the entire link list.
                    desc_and_link = split.split('|')
                    description = desc_and_link[0].strip()
                    link = desc_and_link[1].strip()
                    output_with_html += '<li><a href="' + link + '">' + description + '</a></li>'

            output_with_html += '</ul></div>'
            parsed_text = parsed_text.replace(output_with_brackets, output_with_html)
    return parsed_text
