import os
import subprocess


test_list = subprocess.check_output('/home/aron/Dropbox-Uploader/dropbox_uploader.sh list /notemaster_backups', shell=True)
list_output = test_list.decode()
split_list = list_output.split('\n')
document_list = []
tag_list = []

for x in split_list:
    if 'documents' in x:
        doc_name = x.split(' ')[-1]
        document_list.append(doc_name)
    if 'tags' in x:
         tag_name = x.split(' ')[-1]
         tag_list.append(tag_name)

document_list.sort()
tag_list.sort()
newest_doc = document_list[-1]
newest_tag = tag_list[-1]
#print(document_list[-1])
#print(tag_list[-1])