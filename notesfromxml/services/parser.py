from ..models import Tag, Document, Tagmap, ImageTagMap, Image
import re


def parser_main(parsed_text):
    parsed_text = hyperlink_parser(parsed_text)
    parsed_text = java_code_parser(parsed_text)
    parsed_text = image_insert_parser(parsed_text)
    parsed_text = links_to_table_parser(parsed_text)
    parsed_text = tagged_docs_to_list_parser(parsed_text)
    return parsed_text


def hyperlink_parser(parsed_text):
    pattern = r'\[\[\[(.*?)\]\]\]'

    matches = re.finditer(pattern, parsed_text)
    if matches is not None:
        for match in set(matches):
            #print(match)
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


def tagged_docs_to_list_parser(parsed_text):
    pattern = re.compile(r'\[list\[\[(.*?)\]\]\]', re.DOTALL)
    matches = re.finditer(pattern, parsed_text)
    if matches is not None:
        for match in matches:
            excluded_tags = ''
            output_with_html = '<div class="document-list"> <p class="document-list-header">Documents</p> <ul>'
            output_with_brackets = match.group()
            output_without_brackets = re.search(pattern, parsed_text).group(1).strip()

            if '|' in output_without_brackets:
                split_output = output_without_brackets.split('|')
                matched_tag_name = split_output[0].strip()
                excluded_tags = [x.strip() for x in split_output[1].split(',')]
            else:
                matched_tag_name = output_without_brackets
            if Tag.objects.filter(tag_name=matched_tag_name).exists():
                current_tag = Tag.objects.get(tag_name=matched_tag_name)
                tagmap_set = current_tag.tagmap_set.all()
                for tagmap in tagmap_set:
                    name = tagmap.document.document_name
                    if excluded_tags != '':
                        for tag in excluded_tags:
                            if tag != name:
                                output_with_html += '<li><a href="/notesfromxml/displaydoc/' + name \
                                                    + '">' + name + '</a></li>'
                    else:
                        output_with_html += '<li><a href="/notesfromxml/displaydoc/' + name \
                                            + '">' + name + '</a></li>'
            output_with_html += '</ul></div>'
            parsed_text = parsed_text.replace(output_with_brackets, output_with_html)
    return parsed_text
