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
    res['source'] = maxim_type
    res['maximes'] = []
    for m in maximes:
        res['maximes'].append(dataclasses.asdict(m))
    return res


def do_work(args):
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


def parse_common(tree, total_num, number_block_offset, text_block_offset, number_block_template, text_block_template):
    for n in range(1, total_num + 1):
        number_block_idx = n + number_block_offset
        text_block_idx = n + text_block_offset

        number_block_path = number_block_template.format(number_block_idx)
        text_block_path = text_block_template.format(text_block_idx)

        parsed_number = tree.xpath(number_block_path)[0]
        parsed_text = tree.xpath(text_block_path)[0]
        m = MaximeItem(int(parsed_number), parsed_text)
        yield m


def parse_default(tree):

    number_block_offset = 0
    text_block_offset = 2

    TOTAL_NUM = 504
    number_block_template = '//*[@id="mw-content-text"]/div/div[4]/h3[{}]/span/text()'
    text_block_template = '//*[@id="mw-content-text"]/div/div[4]/p[{}]/text()'

    yield from parse_common(tree, TOTAL_NUM, number_block_offset, text_block_offset, number_block_template, text_block_template)


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

    do_work(args)


main()
