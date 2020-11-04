#!/usr/bin/env python
import argparse
import json
import requests

BLOG_ID = '185133231'

API_BASE = 'https://public-api.wordpress.com/rest/v1.1'

CATEGORY_DEFAULT = 'reflexions-morales'
CATEGORY_SUPPRIMEES = 'maximes-supprimees'
CATEGORY_POSTHUMES = 'maximes-posthumes'


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
        return requests.post(url, params=params, headers=headers, data=data)


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
    resp = make_post(
        token,
        title=get_title(category_str, id),
        content=text,
        slug=get_slug(category_str, id),
        category=get_category(category_str)
    )
    print(resp.status_code)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--authfile')
    parser.add_argument('--maximes', required=True)
    parser.add_argument('--source', required=True,
                        choices=('default', 'posthumes', 'supprimees'))
    args = parser.parse_args()
    print(args)
    token = get_token(args.authfile)

    with open(args.maximes) as maximes_file:
        maximes_json = json.load(maximes_file)

    assert maximes_json['source'] == args.source
    print(f'file opened {args.maximes}, type {args.source}')
    category_str = args.source

    post_maxim(maximes_json['maximes'][0], token, category_str)


main()
