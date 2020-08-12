import os
from django.test.testcases import TestCase
from pathlib import Path
import subprocess


class DropboxTests(TestCase):

    def test_list_files(self):
        this_path = Path(os.path.dirname(os.path.realpath(__file__)))
        print(this_path)
        print(this_path.parent)
        dropbox_util_path =Path(this_path.parent / 'utils' / 'dropbox_backup_util' / 'Dropbox-Uploader' / 'dropbox_uploader.sh')
        print(dropbox_util_path)
        #list_string =

        #test_list = os.system(str(dropbox_util_path) + ' list')
        #test_list = subprocess.check_output((str(dropbox_util_path) + ' list'), shell=True)
        command = str(dropbox_util_path) + ' list'
        #test_list = subprocess.getoutput(command)
        #print(test_list)
        print(dropbox_util_path)

        #test_list = subprocess.check_output(command, shell=True)
        #print(test_list)

        #test_list = subprocess.Popen(str(dropbox_util_path) + ' list', shell=True, stdout=subprocess.PIPE).stdout
        #print('testest1')
        #print(test_list)
        #test_list_string = test_list.read()
        #print(test_list.read())
        #print(test_list.read().decode())
        #print(test_list_string.decode())
        #print('testest2')

        # WHY WONT THIS WORK???
        test_list = subprocess.Popen(['cmd.exe', str(dropbox_util_path), 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).stdout
        print(test_list)
        print(test_list.read())
        #print(test_list.stdout)
        #print(test_list.stdout.read())
        #test_list = os.system(str(dropbox_util_path) + ' info')
        #print(test_list.stdout.read())
