from ..models import Tag, Document, Tagmap, ImageTagMap, Image
import re
from django.template import loader


class TextParser:

    pattern = ''

    def __init__(self):
        self.pattern = re.compile(r'\[([a-zA-Z0-9]*)\[\[(.*?)\]\]\]', re.DOTALL)

    def perform_parse(self, input_text):

        parsed_text = input_text
        while self.is_match(parsed_text):
            parsed_text = self.find_match(parsed_text)
        return parsed_text

    def find_match(self, input_text):
        matches = re.finditer(self.pattern, input_text)
        if matches is not None:  # If match is found.
            for match in matches:
                entire_match = match.group()
                matched_type = match.group(1)
                matched_text = match.group(2)
                string_to_cut = '[' + matched_type + '[['  # Cut the [[[ in front but not the ]]] in back
                cut_string = entire_match[len(string_to_cut):]

                if self.is_match(cut_string):  # If a match is found inside the match.
                    new_matched_text = self.find_match(cut_string)  # Recurse
                    # Replace the text plus ]]] and return it so the match inside the match is properly parsed.
                    input_text = input_text.replace(matched_text + ']]]', new_matched_text)
                    return input_text

                input_text = self.handle_parsing(input_text, entire_match, matched_text, matched_type)
                return input_text

        return input_text  # Todo: I don't know if this is ever reached.

    def handle_parsing(self, input_text, text_with_brackets, text_without_brackets, text_type):
        output_text = input_text

        if text_type.strip() == '':
            output_text = self.hyperlink_parser(input_text, text_with_brackets, text_without_brackets)
        elif text_type == 'java':
            output_text = self.java_code_parser(input_text, text_with_brackets, text_without_brackets)
        elif text_type == 'image':
            output_text = self.image_insert_parser(input_text, text_with_brackets, text_without_brackets)
        elif text_type == 'links':
            output_text = self.link_to_table_parser(input_text, text_with_brackets, text_without_brackets)
        elif text_type == 'list':
            output_text = self.tagged_docs_to_list_parser(input_text, text_with_brackets, text_without_brackets)
        elif text_type == 'esc':
            output_text = self.escape_parser(input_text, text_with_brackets, text_without_brackets)

        return output_text

    def hyperlink_parser(self, input_text, text_with_brackets, text_without_brackets):
        output_text = input_text
        if '|' in text_without_brackets:
            split_output = text_without_brackets.split('|')
            document_name = split_output[0].strip()
            document_parameters = split_output[1].strip()
        else:
            document_name = text_without_brackets
            document_parameters = text_without_brackets
        if Document.objects.filter(document_name=document_name).exists():
            document = Document.objects.filter(document_name=document_name).get()
            output_with_link = '<a href="/notemaster/document/' + str(document.id) \
                               + '">' + document_parameters + '</a>'
        else:
            output_with_link = '<a href="/notemaster/document/' + str(0) \
                               + '" class="broken-link">' + document_parameters + '</a>'
        output_text = output_text.replace(text_with_brackets, output_with_link)
        return output_text

    def java_code_parser(self, input_text, text_with_brackets, text_without_brackets):
        output_text = input_text
        output_with_html = '<pre><code class="language-java" data-lang="java">' + text_without_brackets \
                           + '</code></pre>'
        output_text = output_text.replace(text_with_brackets, output_with_html)
        return output_text

    def image_insert_parser(self, input_text, text_with_brackets, text_without_brackets):
        """
        The part of the parser that handles images. It converts the input into displayable images in the text.
        TODO comment this.
        :param input_text:
        :param text_with_brackets:
        :param text_without_brackets:
        :return:
        """
        output_text = input_text
        image_name = ''
        style_string = ''  # String added to the HTML to apply style to the image.
        no_text = False  # Determines if the text in the card for the image should be displayed or not.
        #output_with_brackets = match.group()  # Example: [image[[My Image]]]
        #output_without_brackets = re.search(pattern, parsed_text).group(1).strip()  # Example: My Image

        if '|' in text_without_brackets:
            split_output = text_without_brackets.split('|')
            image_name = split_output[0].strip()
            image_parameters = [x.strip() for x in split_output[1].split(',')]
            for parameter in image_parameters:
                if 'side' in parameter:  # Which side should the image be on?
                    style_string += 'float:' + parameter.split('=')[1].strip() + ';'
                if 'width' in parameter:  # How large should the image be?
                    style_string += 'width:' + parameter.split('=')[1].strip() + 'px;'
                if 'no_text' in parameter:  # Should we display text with the image or not?
                    no_text = True

        else:
            image_name = text_without_brackets

        if Image.objects.filter(image_name=image_name).exists():
            image = Image.objects.get(image_name=image_name)
            # Gets the html from a snippet as a string and inserts all relevant variables into it.
            output_with_html = loader.render_to_string('notes/snippets/display-image-card.html',
                                                       {'image': image, 'style_string': style_string,
                                                        'no_text': no_text})
            output_text = output_text.replace(text_with_brackets, output_with_html)
        else:
            #output_text = f'<p style="color: red;">No image with the name ({image_name}) was found.</p>'
            output_with_html = loader.render_to_string(
                'notes/snippets/error-parser-snippet.html',
                    {'error_message': f'No image with the name ({image_name}) was found.'})
            output_text = output_text.replace(text_with_brackets, output_with_html)
        return output_text

    def link_to_table_parser(self, input_text, text_with_brackets, text_without_brackets):
        output_text = input_text
        output_with_html = '<div class="link-list"> <p class="link-list-header">Links</p> <ul>'
        split_output = text_without_brackets.split(';')
        for split in split_output:
            if split.strip() != '':  # If ; is at the end of the entire link list.
                if '|' in split:
                    desc_and_link = split.split('|')
                    description = desc_and_link[0].strip()
                    link = desc_and_link[1].strip()
                    output_with_html += '<li><a href="' + link + '">' + description + '</a></li>'

        output_with_html += '</ul></div>'
        output_text = output_text.replace(text_with_brackets, output_with_html)
        return output_text

    def tagged_docs_to_list_parser(self, input_text, text_with_brackets, text_without_brackets):
        output_text = input_text
        excluded_tags = ''
        output_with_html = '<div class="document-list"> <p class="document-list-header">Documents</p> <ul>'

        if '|' in text_without_brackets:
            split_output = text_without_brackets.split('|')
            matched_tag_name = split_output[0].strip()
            excluded_tags = [x.strip() for x in split_output[1].split(',')]
        else:
            matched_tag_name = text_without_brackets
        if Tag.objects.filter(tag_name=matched_tag_name).exists():
            current_tag = Tag.objects.get(tag_name=matched_tag_name)
            tagmap_set = current_tag.tagmap_set.all()
            for tagmap in tagmap_set:
                name = tagmap.document.document_name
                if excluded_tags != '':
                    for tag in excluded_tags:
                        if tag != name:
                            output_with_html += '<li><a href="/notemaster/document/' + name \
                                                + '">' + name + '</a></li>'
                else:
                    output_with_html += '<li><a href="/notemaster/document/' + name \
                                        + '">' + name + '</a></li>'
        output_with_html += '</ul></div>'
        output_text = output_text.replace(text_with_brackets, output_with_html)
        return output_text

    def escape_parser(self, input_text, text_with_brackets, text_without_brackets):
        output_text = input_text
        text_without_brackets = text_without_brackets.replace('<', '&lt;')
        text_without_brackets = text_without_brackets.replace('>', '&gt;')
        output_text = output_text.replace(text_with_brackets, text_without_brackets)
        return output_text

    def is_match(self, input_text):
        matches = re.finditer(self.pattern, input_text)
        # Returns true if there is any element in the iterator without removing the element.
        return any(True for _ in matches)
