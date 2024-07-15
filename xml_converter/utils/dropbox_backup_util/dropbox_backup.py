from pathlib import Path
import os
import datetime


class DropboxSync:

    uploader_path = ''
    xml_doc_path = ''
    xml_tag_path = ''
    extension = ''

    def __init__(self, extension='.xml'):
        this_path = Path(os.path.dirname(os.path.realpath(__file__)))
        xml_path = Path(this_path / 'downloaded_xml/')
        if not xml_path.exists():
            xml_path.mkdir()
        self.uploader_path = Path(this_path / 'Dropbox-Uploader' / 'dropbox_uploader.sh')
        self.xml_doc_path = Path(xml_path / 'documents.xml')
        self.xml_tag_path = Path(xml_path / 'tags.xml')
        self.extension = extension  # Mostly used for test purposes, to add .test after files that are tests.
        self.xml_on_server_path = 'einsk.is:8080/notemaster/xml/'

    def download_xml(self):
        """ Gets the newest version of the xml for documents and tags. """

        # curl -o documents.xml einsk.is:8080/notemaster/xml/documents/
        os.system('curl -o ' + str(self.xml_doc_path) + ' ' + self.xml_on_server_path +  'documents/')

        # os.system('curl -o tags.xml einsk.is:8080/notemaster/xml/tags/')
        # os.system('/home/aron/Dropbox-Uploader/dropbox_uploader.sh upload /home/aron/dropbox_backup_test/tags.xml notemaster_backups/tags_' + current_date + '.xml')

        # curl -o tags.xml einsk.is:8080/notemaster/xml/tags/
        # os.system('curl -o ' + str(self.xml_tag_path) + ' einsk.is:8080/notemaster/xml/tags/')
        os.system('curl -o ' + str(self.xml_tag_path) + ' ' + self.xml_on_server_path  + 'tags/')

    def upload_xml_to_dropbox(self):
        """ Uploads the xml documents and tags to dropbox. It assumes that download_xml has already run. """

        d = datetime.datetime.today()
        current_date = d.strftime('%Y-%m-%d')

        # /opt/notemaster/xml_converter/utils/dropbox_backup_util/dropbox_uploader.sh upload /opt/notemaster/xml_converter/utils/dropbox_backup_util/downloaded_xml/documents.xml notemaster_backups/documents_' + current_date + '.xml
        doc_upload_string = str(self.uploader_path) + ' upload ' + str(
            self.xml_doc_path.as_posix()) + ' notemaster_backups/documents_' + current_date + self.extension
        os.system(doc_upload_string)

        # /opt/notemaster/xml_converter/utils/dropbox_backup_util/dropbox_uploader.sh upload /opt/notemaster/xml_converter/utils/dropbox_backup_util/downloaded_xml/tags.xml notemaster_backups/tags_' + current_date + '.xml
        tag_upload_string = str(self.uploader_path) + ' upload ' + str(
            self.xml_tag_path.as_posix()) + ' notemaster_backups/tags_' + current_date + self.extension
        os.system(tag_upload_string)

    def perform_upload(self):
        self.download_xml()
        self.upload_xml_to_dropbox()

    @DeprecationWarning
    def download_xml_old(self):
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
    syncer = DropboxSync()
    syncer.xml_on_server_path = 'http://localhost:8000/notemaster/xml/'
    syncer.download_xml()
    #syncer.download_xml()
    #syncer.perform_upload()
