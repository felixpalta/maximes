#!/usr/bin/env python
import argparse
import json
import requests

BLOG_ID = '185133231'

API_BASE = 'https://public-api.wordpress.com/rest/v1.1'


def make_me_route():
    return API_BASE + "/me"


def make_site_route(site_route):
    return f'{API_BASE}/{BLOG_ID}/sites/{site_route}'


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--authfile')
    args = parser.parse_args()
    print(args)
    token = get_token(args.authfile)
    # print('token', token)

    resp = rq('GET', make_me_route(), token)
    resp.raise_for_status()
    print(resp.json())


main()
