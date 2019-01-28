import hashlib
import json
import os

import requests
from requests.exceptions import HTTPError


BASE_URL = 'https://api.figshare.com/v2/{endpoint}'
TOKEN = 'b53a73d6d7600ae1c49728b36ea4c5c5f7f02787ab0e9ecdcce52ad640c2a4f7b9c15c85bf54e24be626d08139b9db6e7a602a8f913d2a76765103bbea0c2f1c'
CHUNK_SIZE = 1048576



def raw_issue_request(method, url, data=None, binary=False):
    headers = {'Authorization': 'token ' + TOKEN}
    if data is not None and not binary:
        data = json.dumps(data)
    response = requests.request(method, url, headers=headers, data=data)
    try:
        response.raise_for_status()
        try:
            data = json.loads(response.content.decode("utf-8"))
        except ValueError:
            data = response.content
    except HTTPError as error:
        try:
            print('Caught an HTTPError: {}'.format(error.message))
        except:
            pass
        
        print('Response:',response)
        print('Body:\n', response.content.decode("utf-8"))
        raise

    return data


def issue_request(method, endpoint, *args, **kwargs):
    return raw_issue_request(method, BASE_URL.format(endpoint=endpoint), *args, **kwargs)


def list_articles():
    result = issue_request('GET', 'account/articles')
    print('Listing current articles:')
    if result:
        for item in result:
            print('  {url} - {title}'.format(**item))
    else:
        print('  No articles.')
    print()


def create_article(title):
    data = {
        'title': title,  # You may add any other information about the article here as you wish.
        'defined_type':'fileset',
        'tags':['Eye-tracking', 'eye tracking', 'pupil labs', 'eyelink 1000', 'eye movements', 'smooth pursuit', 'blinks', 'saccades', 'benchmark', 'accuracy', 'precision', 'test battery', 'pupil dilation', 'head movement', 'free viewing', 'microsaccades', 'eyetracking','eyetracker'],
        'authors':[{"id": 6064694},{'name':"Katharina Groß"},{'name':'Inga Ibs'},{'name':'Peter König'}]}
    result = issue_request('POST', 'account/articles', data=data)
    print('Created article:', result['location'], '\n')

    result = raw_issue_request('GET', result['location'])

    return result['id']


def list_files_of_article(article_id):
    result = issue_request('GET', 'account/articles/{}/files'.format(article_id))
    print('Listing files for article {}:'.format(article_id))
    if result:
        for item in result:
            print('  {id} - {name}'.format(**item))
    else:
        print('  No files.')

    print()


def get_file_check_data(file_name):
    with open(file_name, 'rb') as fin:
        md5 = hashlib.md5()
        size = 0
        data = fin.read(CHUNK_SIZE)
        while data:
            size += len(data)
            md5.update(data)
            data = fin.read(CHUNK_SIZE)
        return md5.hexdigest(), size


def initiate_new_upload(article_id, file_name):
    endpoint = 'account/articles/{}/files'
    endpoint = endpoint.format(article_id)
    print('calculating md5, might take a while for large files')
    md5, size = get_file_check_data(file_name)
    print('md5 done')
    data = {'name': os.path.basename(file_name),
            'md5': md5,
            'size': size}

    result = issue_request('POST', endpoint, data=data)
    print('Initiated file upload:', result['location'], '\n')

    result = raw_issue_request('GET', result['location'])

    return result


def complete_upload(article_id, file_id):
    issue_request('POST', 'account/articles/{}/files/{}'.format(article_id, file_id))


def upload_parts(FILE_PATH,file_info):
    url = '{upload_url}'.format(**file_info)
    result = raw_issue_request('GET', url)

    print('Uploading parts:')
    with open(FILE_PATH, 'rb') as fin:
        for part in result['parts']:
            upload_part(file_info, fin, part)
    print()


def upload_part(file_info, stream, part):
    udata = file_info.copy()
    udata.update(part)
    url = '{upload_url}/{partNo}'.format(**udata)

    stream.seek(part['startOffset'])
    data = stream.read(part['endOffset'] - part['startOffset'] + 1)

    raw_issue_request('PUT', url, data=data, binary=True)
    print('  Uploaded part {partNo} from {startOffset} to {endOffset}'.format(**part))


def file_to_figshare(TITLE,FILE_PATH,article_id=None):
    # We first create the article
    if article_id is None:
        list_articles()   
        article_id = create_article(TITLE)
    list_articles()
    list_files_of_article(article_id)

    # Then we upload the file.
    file_info = initiate_new_upload(article_id, FILE_PATH)
    # Until here we used the figshare API; following lines use the figshare upload service API.
    upload_parts(FILE_PATH,file_info)
    # We return to the figshare API to complete the file upload process.
    complete_upload(article_id, file_info['id'])
    list_files_of_article(article_id)
    return(article_id)


