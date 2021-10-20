import argparse
from regex_parser import RegexParser


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse regular expressions and test words againt them"
    )
    parser.add_argument("regex", help="the non-empty regex to be parsed", type=str)

    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_arguments()
    regex = args.regex
    parser = RegexParser(regex)
    print(f"Raw regex in infix notation:\t\t {parser.raw_regex}")
    print(f"Purified regex in infix notation:\t {parser.purified_regex}")
    print(f"Preprocessed regex in infix notation:\t {parser.preprocessed_regex}")
    print(f"Converted regex in postfix notation:\t {parser.converted_regex}")
    print(parser.expression_tree)
    print(parser.nfa)
