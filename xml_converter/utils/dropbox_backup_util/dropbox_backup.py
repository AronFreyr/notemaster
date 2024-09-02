from pathlib import Path
import os
import datetime
import configparser
import requests
from bs4 import BeautifulSoup
import shutil
import filecmp


class DropboxSync:

    uploader_path = ''
    xml_doc_path = ''
    xml_tag_path = ''
    extension = ''

    def __init__(self, extension='.xml', config_location=None):
        self.parser = configparser.ConfigParser(allow_no_value=True)
        self.parser.read(config_location)
        host_name = self.parser['XML_CONVERTER']['XML_HOSTNAME']
        this_path = Path(os.path.dirname(os.path.realpath(__file__)))
        self.xml_path = Path(this_path / 'downloaded_xml/')
        if not self.xml_path.exists():
            self.xml_path.mkdir()
        self.uploader_path = Path(this_path / 'Dropbox-Uploader' / 'dropbox_uploader.sh')
        self.xml_doc_path = Path(self.xml_path / 'documents.xml')
        self.xml_tag_path = Path(self.xml_path / 'tags.xml')
        self.extension = extension  # Mostly used for test purposes, to add .test after files that are tests.
        self.xml_on_server_path = host_name + '/notemaster/xml/'
        self.login_url = host_name + '/accounts/login/'
        self.session: requests.Session = None

    def __del__(self):
        if self.session:
            self.session.close()


    def login_procedure(self):
        session = requests.session()
        response = session.get(self.login_url)
        response.raise_for_status()

        # Retrieve CSRF token
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

        # log in
        payload = {
            'username': self.parser['XML_CONVERTER']['XML_USERNAME'],
            'password': self.parser['XML_CONVERTER']['XML_PASSWORD'],
            'csrfmiddlewaretoken': csrf_token
        }
        headers = {'Referer': self.login_url}
        response = session.post(self.login_url, data=payload, headers=headers)
        if response.ok:
            self.session = session
        else:
            raise AttributeError('Unable to create login session for data retrieval.')


    def download_xml(self, xml_type: str):
        """ Gets the newest version of the xml for documents and tags. """

        # curl -o documents.xml einsk.is:8080/notemaster/xml/documents/
        os.system('curl -o ' + str(self.xml_path / (xml_type + '.xml')) + ' ' + self.xml_on_server_path + xml_type +  '/')

        # os.system('curl -o tags.xml einsk.is:8080/notemaster/xml/tags/')
        # os.system('/home/aron/Dropbox-Uploader/dropbox_uploader.sh upload /home/aron/dropbox_backup_test/tags.xml notemaster_backups/tags_' + current_date + '.xml')

        # curl -o tags.xml einsk.is:8080/notemaster/xml/tags/
        # os.system('curl -o ' + str(self.xml_tag_path) + ' einsk.is:8080/notemaster/xml/tags/')
        os.system('curl -o ' + str(self.xml_tag_path) + ' ' + self.xml_on_server_path  + 'tags/')

    def download_xml_with_session(self, xml_type: str):
        if not self.session:
            self.login_procedure()

        if not self.session:  # Something must have gone wrong in the login procedure.
            raise AttributeError('There is no logged in session. Something went wrong in the login procedure.')

        data = self.session.get(self.xml_on_server_path + xml_type + '/')

        if data.ok:
            with open(str(self.xml_path / (xml_type + '.xml')), 'w', encoding='utf-8') as f:
                f.write(data.text)
        else:
            raise AttributeError(f'Unable to download data from the server for document type=({xml_type})')

    def upload_xml_to_dropbox(self, xml_type: str, upload_flag: bool=True):
        """ Uploads the xml documents and tags to dropbox. It assumes that download_xml has already run. """

        d = datetime.datetime.today()
        current_date = d.strftime('%Y-%m-%d')

        xml_file = self.xml_path / (xml_type + self.extension)
        xml_old_file = self.xml_path / (xml_type + '_latest' + self.extension)
        if not xml_file.exists():
            raise FileExistsError(f'Could not find any file at {xml_file.as_posix()}')

        if not xml_old_file.exists():
            xml_old_file.touch()  # Creates an empty file.

        no_change = filecmp.cmp(xml_file.as_posix(), xml_old_file.as_posix())

        if not no_change:
            shutil.copy(xml_file.as_posix(), xml_old_file.as_posix())

        # /opt/notemaster/xml_converter/utils/dropbox_backup_util/dropbox_uploader.sh upload /opt/notemaster/xml_converter/utils/dropbox_backup_util/downloaded_xml/documents.xml notemaster_backups/documents_' + current_date + '.xml
            upload_string = str(self.uploader_path) + ' upload ' + str(
                (self.xml_path / (xml_type + self.extension)).as_posix()
                + ' notemaster_backups/' + xml_type + '_' + current_date + self.extension
            )
            if upload_flag:
                os.system(upload_string)

    def perform_upload(self, data_to_upload):
        self.login_procedure()
        for data in data_to_upload:
            self.download_xml_with_session(data)
            self.upload_xml_to_dropbox(data)

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
    conf_location = Path(__file__).resolve().parent.parent.parent.parent / 'notemaster' / 'config' / 'dev.ini'
    syncer = DropboxSync(config_location=conf_location)
    #syncer.xml_on_server_path = 'http://localhost:8000/notemaster/xml/'
    #syncer.download_xml()
    # syncer.download_xml_with_session('documents')
    what_to_upload = ['documents', 'tags']
    syncer.perform_upload(what_to_upload)
