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
    out_file_prefix = type_data[1]
    if use_ascii:
        out_file_prefix += '_ascii'

    with open(html_file_name, encoding='utf8') as input_html:
        tree = html.fromstring(input_html.read())
        maximes = parser(tree)

    maximes_json = json.dumps(maximes_to_dict(
        maxim_type, maximes), ensure_ascii=use_ascii)

    if dry_run:
        print(maximes_json)
    else:
        store_to_file(maximes_json, out_file_prefix)


def store_to_file(maximes_json, out_file_prefix):
    out_file_name = out_file_prefix + '.json'
    with open(out_file_name, 'w', encoding='utf8') as out_file:
        out_file.write(maximes_json)


def parse_default(tree):

    number_block_offset = 0
    text_block_offset = 2

    TOTAL_NUM = 504
    for n in range(1, TOTAL_NUM + 1):
        number_block_idx = n + number_block_offset
        text_block_idx = n + text_block_offset

        parsed_number = tree.xpath(
            f'//*[@id="mw-content-text"]/div/div[4]/h3[{number_block_idx}]/span/text()')[0]
        parsed_text = tree.xpath(
            f'//*[@id="mw-content-text"]/div/div[4]/p[{text_block_idx}]/text()'
        )[0]
        m = MaximeItem(parsed_number, parsed_text)
        yield m


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
