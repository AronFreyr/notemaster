"""
Functions for handling the creation and deletion of objects in the database.
Sometimes that means disassociating them from other objects, sometimes it means deleting them entirely.
"""

from notes.models import Tag, Document, Tagmap, ImageTagMap, Image
from timemaster.models import IntervalTagMap


def handle_new_tag(new_tags: str, tag_creator=None, new_doc=None,
                   new_image=None, new_interval=None, tag_type:tuple=None):
    # TODO: Update documentation for ImageTagMaps.
    # TODO: Create functionality for DocumentTagMaps.
    """
    Function for handling the creation of new tags, adding them to the document and saving them in the database.
    :param new_tags: Tags to be added to a document. The tag may already be in the database but not yet associated
     with the document that we want to link it to.
    :param new_doc: If we are creating a new document at the same time we are creating a new tag, we need to create
     a newtagmap as well.
    :return: nothing.
    """
    if new_tags == '':
        return
    # Tags are separated by a comma (,) but if there is a comma in the tag name then it can be escaped with this trick.
    new_tags = new_tags.replace(r'\,', 'replacecommahackfromhell')
    split_tags = new_tags.split(',')
    for new_tag in split_tags:
        new_tag = new_tag.replace('replacecommahackfromhell', ',').strip()
        if Tag.objects.filter(tag_name=new_tag).exists():  # If the tag already exists.
            current_tag = Tag.objects.get(tag_name=new_tag)
        else:  # Create the new tag and save it in the database.
            if new_tag != '' and new_tag != '"':
                if tag_type:
                    input_tag_type = tag_type[0]
                    input_meta_tag_type = tag_type[1]
                else:
                    input_tag_type = 'normal'
                    input_meta_tag_type = 'none'
                current_tag = Tag(tag_name=new_tag, tag_created_by=tag_creator, tag_last_modified_by=tag_creator,
                                  tag_type=input_tag_type, meta_tag_type=input_meta_tag_type)
                current_tag.save()
        if new_doc:  # If we are adding a tag to a newly created document.
            # If the tagmap for the newly created document and the tag does not exist.
            if not Tagmap.objects.filter(tag=current_tag, document=new_doc).exists():
                new_tagmap = Tagmap(document=new_doc, tag=current_tag)
                new_tagmap.save(using='default')
        if new_image:
            if not ImageTagMap.objects.filter(tag=current_tag, image=new_image).exists():
                new_image_tagmap = ImageTagMap(image=new_image, tag=current_tag)
                new_image_tagmap.save()
        if new_interval:
            if not IntervalTagMap.objects.filter(tag=current_tag, interval=new_interval).exists():
                new_interval_tagmap = IntervalTagMap(tag=current_tag, interval=new_interval)
                new_interval_tagmap.save()


def delete_object(obj_id: int, obj_type: str):
    """
    Deletes objects from the database based on their type. Also removes all tag maps associated with the object.
    :param obj_id: The object ID to be deleted.
    :param obj_type: The type of the object to be deleted. Can be 'tag', 'document', or 'image'.
    :return: Nothing
    """
    # TODO: refactor this. We can handle all types of objects in the same way.
    # TODO: Make some tests for this before the refactor.
    if obj_type == 'tag':  # If we are deleting a tag.
        tag_to_delete = Tag.objects.get(id=obj_id)
        for tagmap in tag_to_delete.tagmap_set.all():
            tagmap.delete()
        tag_to_delete.delete()
    elif obj_type == 'document':  # If we are deleting a document.
        doc_to_delete = Document.objects.get(id=obj_id)
        for tagmap in doc_to_delete.tagmap_set.all():
            tagmap.delete()
        doc_to_delete.delete()
    elif obj_type == 'image':  # If we are deleting an image.
        img_to_delete = Image.objects.get(id=obj_id)
        for tagmap in img_to_delete.imagetagmap_set.all():
            tagmap.delete()
        img_to_delete.delete()


def remove_object(obj_id: int, obj_type: str, request):
    """
    Disconnects documents from tags and vice versa.
    This does not delete the objects, but does delete the tag map that connects them.
    :param obj_id: The ID of the object to be removed.
    :param obj_type: The type of the object to be removed. Can be 'tag' or 'document'.
    :param request: Django request object, used to get the currently viewed document or tag.
    :return: Nothing
    """
    if obj_type == 'tag':
        tag_to_remove = Tag.objects.get(id=obj_id)
        document = Document.objects.get(document_name=request.POST['currently_viewed_doc'])
        tagmap_to_delete = tag_to_remove.tagmap_set.get(tag=tag_to_remove, document=document)
        tagmap_to_delete.delete()
    elif obj_type == 'document':
        doc_to_remove = Document.objects.get(id=obj_id)
        current_tag = Tag.objects.get(tag_name=request.POST['currently_viewed_tag'])
        tagmap_to_delete = doc_to_remove.tagmap_set.get(tag=current_tag, document=doc_to_remove)
        tagmap_to_delete.delete()
