#!/usr/bin/env python
import argparse
import json
import requests
import time

BLOG_ID = '185133231'

API_BASE = 'https://public-api.wordpress.com/rest/v1.1'

CATEGORY_DEFAULT = 'maximes'
CATEGORY_SUPPRIMEES = 'supprimees'
CATEGORY_POSTHUMES = 'posthumes'


def get_category(category_str):
    return {
        'default': CATEGORY_DEFAULT, 'posthumes': CATEGORY_POSTHUMES, 'supprimees': CATEGORY_POSTHUMES
    }[category_str]


def get_slug(category_str, id):
    return {
        'default': f'maximes-{id}', 'posthumes': f'posthumes-{id}', 'supprimees': f'supprimees-{id}'
    }[category_str]


def get_title(category_str, id):
    return {
        'default': f'Maximes {id}', 'posthumes': f'Posthumes {id}', 'supprimees': f'Supprimées {id}'
    }[category_str]


def make_me_route():
    return API_BASE + "/me"


def make_site_route(site_route):
    return f'{API_BASE}/sites/{BLOG_ID}/{site_route}'


def get_token(authfile: str):
    with open(authfile) as f:
        data = json.load(f)
        return data['access_token']


def make_auth_headers(token: str):
    return {'Authorization': f'BEARER {token}'}


def rq(method: str, url, token, params=None, data=None):
    headers = make_auth_headers(token)
    # print(url)
    # print(headers)
    if method == 'GET':
        return requests.get(url, params=params, headers=headers)
    if method == 'POST':
        headers['Content-Type'] = 'application/json; charset=utf8'
        return requests.post(url, params=params, headers=headers, data=json.dumps(data).encode('utf-8'))


def make_post(token, title, content, slug, category=CATEGORY_DEFAULT):
    url = make_site_route('posts/new')
    data = {'title': title, 'content': content,
            'slug': slug, 'categories': [category], 'likes_enabled': False, 'sharing_enabled': False}
    resp = rq('POST', url, token, data=data)
    resp.raise_for_status()
    return resp


def post_maxim(one_maxim, token, category_str):
    id = one_maxim['idx']
    text = one_maxim['text']
    print(id, text)

    resp = make_post(
        token,
        title=get_title(category_str, id),
        content=text,
        slug=get_slug(category_str, id),
        category=get_category(category_str)
    )
    print(resp.status_code)
    resp_body = resp.json()
    print(resp_body['ID'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--authfile')
    parser.add_argument('--maximes', required=True)
    parser.add_argument('--source', required=True,
                        choices=('default', 'posthumes', 'supprimees'))
    args = parser.parse_args()
    print(args)
    token = get_token(args.authfile)

    with open(args.maximes, encoding='utf-8') as maximes_file:
        maximes_json = json.load(maximes_file)

    assert maximes_json['source'] == args.source
    print(f'file opened {args.maximes}, type {args.source}')
    category_str = args.source

    count = 0
    for one_maxim in maximes_json['maximes']:
        post_maxim(one_maxim, token, category_str)
        count += 1
        if count % 20 == 0:
            print('sleeping...')
            time.sleep(10)

    print(f'{count} uploaded')


main()
