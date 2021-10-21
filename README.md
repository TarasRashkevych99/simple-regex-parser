# Simple Regex Parser

The purpose of this project is to provide a basic implementation of a regex parser that is able to
determine whether or not a word matches a particular regular expression.

## Supported regex operators

The following are the operators that are recognized by the parser :

| Symbol |               Formal Name                | Example |        Description         |
| :----: | :--------------------------------------: | :-----: | :------------------------: |
|   \*   |     Kleene Operator(or Kleene Star)      |   a\*   | 0 or more occurrences of a |
|   \|   | Alternation Operator(or Union Operator)  |  a\|b   |           a or b           |
|   .    | Concatenation Operator(Normally Omitted) |   ab    |      a followed by b       |
|   ()   |           Parenthesis Operator           |   (a)   | a with operator precedence |

## Supported characters

The parser **_should_** allow all possible characters, except for the characters that specify the
operators described above in the table. Moreover, the `ε` character(formally an empty string)
and the `" "` character(useful for typing but useless for processing) are stripped out from the
input word.

## How to run the parser on your machine

Make shure that you have installed the [Python](https://www.python.org/downloads/) 3.7 interpreter or
a higher version of it.<br>
This project has been developed with the Python 3.7.10 interpreter and tested on macOS Big Sur 11.6.
<br>
This project has also been tested on Windows 10 20H2 and Ubuntu 20.04.3.
<br><br>

Clone the repository on your machine :

```
git clone https://github.com/TarasRashkevych99/simple-regex-parser.git
```

Move to the `simple-regex-parser/src` folder by executing the following command :

```
cd simple-regex-parser/src
```

Run inside the `src` folder one the the following command :

```
python run_regex_parser.py regex [-w|--word input_word] [-v|--verbose] [-h|--help]
```

**Note** : on some platforms the name of the Python interpreter might be `python3`.<br>
**Note** : at the moment it is assumed that the `regex` passed in is well-formed(i.d. it
respects the formal definition of the operators).

The arguments have the following meaning:

- `regex` : positional argument that specifies the regex(i.d. the pattern to match against).
- `[-w|--word input_word]` : optional argument where `input_word` specifies the word to be tested
  against the regex.
- `[-v|--verbose]` : optional argument that specifies how detailed the output will be.
- `[-h|--help]` : optional argument that describes the purpose of the program and of each and every
  argument passed to it.

In the case of the `regex` argument, the actual regex can be written by simply escaping the
operators with the `\` character, but it is highly recommended to use double or single quotes
which don't require any type of escaping, like in the following example :

```
python run_regex_parser.py "(r|e|g|e|x)*" -w regex
```

The `[-w|--word input_word]` argument can also be specified by using double or single quotes.

## Example of usage

By executing the following command :

```
python run_regex_parser.py "(r|e|g|e|x)*" -w regex
```

The expected output should be the following :

```
Raw regex in infix notation:             (r|e|g|e|x)*
Generated Expression Tree:
                          |(*):(|)
                          |                             (x)
                          |             (|):(|)(x)
                          |                                             (e)
                          |                             (|):(|)(e)
                          |                                                             (g)
                          |                                             (|):(|)(g)
                          |                                                                             (e)
                          |                                                             (|):(r)(e)
                          |                                                                             (r)

Generated NFA:
        Initial State: (18)
        Final State: ((19))
        States(20): [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        Alphabet(4): {'r', 'e', 'g', 'x'}
        Transition Function(25):
                                (0, 'r') --> [1]
                                (2, 'e') --> [3]
                                (3, 'ε') --> [5]
                                (1, 'ε') --> [5]
                                (4, 'ε') --> [2, 0]
                                (6, 'g') --> [7]
                                (7, 'ε') --> [9]
                                (5, 'ε') --> [9]
                                (8, 'ε') --> [6, 4]
                               (10, 'e') --> [11]
                               (11, 'ε') --> [13]
                                (9, 'ε') --> [13]
                               (12, 'ε') --> [10, 8]
                               (14, 'x') --> [15]
                               (15, 'ε') --> [17]
                               (13, 'ε') --> [17]
                               (16, 'ε') --> [14, 12]
                               (17, 'ε') --> [16, 19]
                               (18, 'ε') --> [16, 19]

The word regex matches the regular expression (r|e|g|e|x)*.

```

## Bug Hunting and Future Maintenance

For bugs, logical errors and feature improvements please create a pull request and let me know what
you have in mind :slightly_smiling_face:.
