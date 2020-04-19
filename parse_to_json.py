from sys import argv
from lxml import html
import dataclasses
import argparse


import json

TYPE_DEFAULT = 'default'
TYPE_POSTHUMES = 'posthumes'
TYPE_SUPPRIMEES = 'supprimees'


@dataclasses.dataclass
class MaximeItem:
    idx: int
    text: str


def error(reason):
    print('Fatal error: ', reason)
    exit(1)


def maximes_to_dict(maxim_type, maximes):
    res = {}
    res['type'] = maxim_type
    res['maximes'] = []
    for m in maximes:
        res['maximes'].append(dataclasses.asdict(m))
    return res


def parse(args):
    maxim_type = args.type
    use_ascii = args.ascii
    html_file_name = args.input_file
    dry_run = args.dry_run

    type_data = PARSER_MAP[maxim_type]
    parser = type_data[0]
    out_file_name = type_data[1]
    if use_ascii:
        out_file_name += '_ascii'

    with open(html_file_name, encoding='utf8') as input_html:
        tree = html.fromstring(input_html.read())
        maximes = parser(tree)

    maximes_json = json.dumps(maximes_to_dict(
        maxim_type, maximes), ensure_ascii=use_ascii)

    if dry_run:
        print(maximes_json)
    else:
        pass


def parse_default(tree):

    number_block_1 = tree.xpath(
        '/html/body/div[3]/div[3]/div[4]/div/div[4]/h3[1]/span/text()')
    text_block_1 = tree.xpath(
        '//*[@id="mw-content-text"]/div/div[4]/p[3]/text()')

    number_block_2 = tree.xpath('//*[@id="mw-content-text"]/div/div[4]/h3[2]')
    text_block_2 = tree.xpath(
        '//*[@id="mw-content-text"]/div/div[4]/p[4]/text()')
    # print(number_block_1[0], text_block_1[0])

    m1 = MaximeItem(number_block_1[0], text_block_1[0])
    return [m1]


def parse_posthumes(tree):
    pass


def parse_supprimees(tree):
    pass


PARSER_MAP = {
    TYPE_DEFAULT: (parse_default, 'maximes'),
    TYPE_POSTHUMES: (parse_posthumes, 'maximes_posthumes'),
    TYPE_SUPPRIMEES: (parse_supprimees, 'maximes_supprimees')
}
########################################################################


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('--type', default=TYPE_DEFAULT)
    parser.add_argument('--ascii', action='store_true')
    parser.add_argument('-n', '--dry-run', action='store_true')
    args = parser.parse_args()
    if args.type not in [TYPE_DEFAULT, TYPE_POSTHUMES, TYPE_SUPPRIMEES]:
        error('invalid type')
    print(args)

    parse(args)


main()
