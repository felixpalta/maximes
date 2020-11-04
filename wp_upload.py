#!/usr/bin/env python
import argparse
import json
import requests
import time

BLOG_ID = ''
TOKEN = ''

API_BASE = 'https://public-api.wordpress.com/rest/v1.1'

CATEGORY_DEFAULT = 'maximes'
CATEGORY_SUPPRIMEES = 'supprimees'
CATEGORY_POSTHUMES = 'posthumes'


def get_category(category_str):
    return {
        'default': CATEGORY_DEFAULT, 'posthumes': CATEGORY_POSTHUMES, 'supprimees': CATEGORY_SUPPRIMEES
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


def set_auth_data(authfile: str):
    global TOKEN
    global BLOG_ID
    with open(authfile) as f:
        data = json.load(f)
        TOKEN = data['access_token']
        BLOG_ID = data['blog_id']


def make_auth_headers(token: str):
    return {'Authorization': f'BEARER {token}'}


def rq(method: str, url, params=None, data=None):
    headers = make_auth_headers(TOKEN)
    if method == 'GET':
        return requests.get(url, params=params, headers=headers)
    if method == 'POST':
        headers['Content-Type'] = 'application/json; charset=utf8'
        return requests.post(url, params=params, headers=headers, data=json.dumps(data).encode('utf-8'))


def make_post(title, content, slug, category=CATEGORY_DEFAULT):
    url = make_site_route('posts/new')
    data = {'title': title, 'content': content,
            'slug': slug, 'categories': [category], 'likes_enabled': False, 'sharing_enabled': False}
    resp = rq('POST', url, data=data)
    resp.raise_for_status()
    return resp


def delete_posts(ids):
    url = make_site_route('posts/delete')
    data = {'post_ids': [str(i) for i in ids]}
    resp = rq('POST', url, data=data)
    resp.raise_for_status()
    return resp


def post_maxim(one_maxim, category_str):
    id = one_maxim['idx']
    text = one_maxim['text']
    print(id, text)

    resp = make_post(
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
    parser.add_argument('--authfile', required=True)
    parser.add_argument('--maximes')
    parser.add_argument('--source',
                        choices=('default', 'posthumes', 'supprimees'))
    parser.add_argument('--delete', nargs='+', type=int)
    parser.add_argument('--delete-range', nargs='+', type=int)

    args = parser.parse_args()

    print(args)
    set_auth_data(args.authfile)

    if args.delete:
        resp = delete_posts(args.delete)
        print(resp.status_code, resp.json())
        return

    if args.delete_range:
        if len(args.delete_range) != 2:
            raise Exception('Delete range must have 2 values')
        delete_from = args.delete_range[0]
        delete_to = args.delete_range[1]
        rng = range(delete_from, delete_to + 1)
        resp = delete_posts(rng)
        print(resp.status_code, resp.json())
        return

    with open(args.maximes, encoding='utf-8') as maximes_file:
        maximes_json = json.load(maximes_file)

    assert maximes_json['source'] == args.source
    print(f'file opened {args.maximes}, type {args.source}')
    category_str = args.source

    count = 0
    for one_maxim in maximes_json['maximes']:
        post_maxim(one_maxim, category_str)
        count += 1
        if count % 20 == 0:
            print('sleeping...')
            time.sleep(10)

    print(f'{count} uploaded')


main()
