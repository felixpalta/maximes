from sys import argv
from lxml import html
import dataclasses
import argparse
import json

"""
This script parses HTML-file, obtained by retrieve.py.
This is a list of "Maximes" by La Rochefoucauld.
There are 3 types of maximes on that page:
- main list (default)
- posthumes
- supprimees
Each Maxime has its own ordinal number, that must be preserved.

The goal is to parse each list of maximes and put in a JSON file.
"""

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
    parser_xpath_generator = type_data[0]
    out_file_prefix = type_data[1]
    if use_ascii:
        out_file_prefix += '_ascii'

    with open(html_file_name, encoding='utf8') as input_html:
        tree = html.fromstring(input_html.read())
        maximes = parse_common(tree, parser_xpath_generator())

    maximes_dict = maximes_to_dict(maxim_type, maximes)
    if dry_run:
        maximes_json = json.dumps(maximes_dict, ensure_ascii=use_ascii)
        print(maximes_json)
    else:
        store_to_file(maximes_dict, out_file_prefix, use_ascii)


def store_to_file(maximes_dict, out_file_prefix, use_ascii):
    out_file_name = out_file_prefix + '.json'
    with open(out_file_name, 'w', encoding='utf8') as out_file:
        json.dump(maximes_dict, out_file, ensure_ascii=use_ascii)


def parse_common(tree, xpath_generator):
    n = 0
    for number_block_path, text_block_path in xpath_generator:
        n += 1
        parsed_number = int(tree.xpath(number_block_path)[0])

        if parsed_number != n:
            raise Exception(
                f'parsed number {parsed_number} does not match loop index {n}')

        parsed_text = tree.xpath(text_block_path)[0]
        m = MaximeItem(parsed_number, parsed_text)
        yield m


def xpath_generator_default():
    number_block_template = '//*[@id="{}"]/text()'
    text_block_template = '//*[@id="mw-content-text"]/div/div[4]/p[{}]/text()'
    for i in range(1, 505):
        number_block_path = number_block_template.format(i)
        text_block_path = text_block_template.format(i + 2)
        yield number_block_path, text_block_path


def xpath_generator_supprimees():
    number_block_template = '//*[@id="{}_2"]/text()'
    text_block_template = '//*[@id="mw-content-text"]/div/div[4]/p[{}]/text()'

    def text_index(i):
        if i < 61:
            return 509 + i
        if i < 62:
            return 511 + i
        return 513 + i

    for i in range(1, 75):
        number_block_path = number_block_template.format(i)
        text_block_path = text_block_template.format(text_index(i))
        yield number_block_path, text_block_path


def xpath_generator_posthumes():
    number_block_template = '//*[@id="{}_3"]/text()'
    text_block_template = '//*[@id="mw-content-text"]/div/div[4]/p[{}]/text()'

    def text_index(i):
        if i < 27:
            return 590 + i
        if i < 32:
            return 592 + i
        if i < 35:
            return 594 + i
        if i < 59:
            return 596 + i
        return 598 + i

    for i in range(1, 62):
        number_block_path = number_block_template.format(i)
        text_block_path = text_block_template.format(text_index(i))
        yield number_block_path, text_block_path


PARSER_MAP = {
    # 0 -> xpath generator
    # 1 -> output file prefix
    TYPE_DEFAULT: (xpath_generator_default, 'maximes'),
    TYPE_POSTHUMES: (xpath_generator_posthumes, 'maximes_posthumes'),
    TYPE_SUPPRIMEES: (xpath_generator_supprimees, 'maximes_supprimees')
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
