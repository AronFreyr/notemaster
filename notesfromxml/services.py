from .models import Tag, Document, Tagmap


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
