from pathlib import Path
import os
import datetime


def download_xml():
    """ Gets the newest version of the xml for documents and tags and uploads it to my dropbox folder. """
    d = datetime.datetime.today()
    current_date = d.strftime('%Y-%m-%d')
    this_path = Path(os.path.dirname(os.path.realpath(__file__)))
    uploader_path = Path(this_path / 'Dropbox-Uploader' / 'dropbox_uploader.sh')
    xml_path = Path(this_path / 'downloaded_xml/')
    xml_doc_path = Path(xml_path / 'documents.xml')

    if not xml_path.exists():
        xml_path.mkdir()

    #os.system('curl -o documents.xml einsk.is:8080/notemaster/xml/documents/')

    os.system('curl -o ' + str(xml_doc_path) + ' einsk.is:8080/notemaster/xml/documents/')
    #os.system('/home/aron/Dropbox-Uploader/dropbox_uploader.sh upload /home/aron/dropbox_backup_test/documents.xml notemaster_backups/documents_' + current_date + '.xml')
    upload_string = str(uploader_path) + ' upload ' + str(xml_doc_path.as_posix()) + ' notemaster_backups/documents_' + current_date + '.xml.test'
    print('upload_string:', upload_string)
    os.system(upload_string)

    #os.system('curl -o tags.xml einsk.is:8080/notemaster/xml/tags/')
    #os.system('/home/aron/Dropbox-Uploader/dropbox_uploader.sh upload /home/aron/dropbox_backup_test/tags.xml notemaster_backups/tags_' + current_date + '.xml')
    xml_tag_path = Path(xml_path / 'tags.xml')
    os.system('curl -o ' + str(xml_tag_path) + ' einsk.is:8080/notemaster/xml/tags/')
    tag_upload_string = str(uploader_path) + ' upload ' + str(xml_tag_path.as_posix()) + ' notemaster_backups/tags_' + current_date + '.xml.test'
    os.system(tag_upload_string)


if __name__ == '__main__':
    download_xml()
