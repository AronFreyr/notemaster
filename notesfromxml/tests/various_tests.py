from django.test.testcases import TestCase
import urllib.request

# Not working. I need to be signed in to dropbox for this to work.
class DropboxTests(TestCase):
    def test_download_from_dropbox(self):
        url = 'https://www.dropbox.com/home/glosur/general.xml?dl=1'
        #url = 'https://dl.dropboxusercontent.com/content_link/moluVccftJLq0UwJkGW3QFZri4OgGPgOzNa7d913SSnnwgoHKFbPYhKCnUhuffgQ/file'
        u = urllib.request.urlopen(url)
        data = u.read()
        u.close()
        print(data)
