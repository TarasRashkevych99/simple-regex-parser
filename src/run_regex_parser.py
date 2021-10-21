import argparse
from regex_parser import RegexParser


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse regular expressions and test words against them"
    )
    parser.add_argument("regex", help="the non-empty regex to be parsed")
    parser.add_argument("--word", "-w", help="the word to be tested against the regex")
    parser.add_argument(
        "--verbose",
        "-v",
        help="add a verbose description of the output",
        action="store_true",
        default=False,
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_arguments()
    regex = args.regex
    word = args.word
    verbose = args.verbose

    parser = RegexParser(regex)

    print(f"Raw regex in infix notation:\t\t {parser.raw_regex}")

    if verbose:
        print(f"Purified regex in infix notation:\t {parser.purified_regex}")
        print(f"Preprocessed regex in infix notation:\t {parser.preprocessed_regex}")
        print(f"Converted regex in postfix notation:\t {parser.converted_regex}")

    print(parser.expression_tree)
    print(parser.nfa)
    print()

    if word:
        if parser.recognize_word(word):
            print(f"The word {word} matches the regular expression {regex}.")
        else:
            print(f"The word {word} doesn't match the regular expression {regex}.")
        print()
