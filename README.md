# Simple Regex Parser

The purpose of this project is to provide a basic implementation of a regex parser that is able to
determine whether or not a word matches a particular regular expression.

## Operators supported by regex

The following are the operators that are recognized by the parser :

| Operator |               Formal Name                | Example |         Description          |
| :------: | :--------------------------------------: | :-----: | :--------------------------: |
|    \*    |     Kleene Operator(or Kleene Star)      |   a\*   |  0 or more occurrences of a  |
|    \|    | Alternation Operator(or Union Operator)  |  a\|b   |            a or b            |
|    .     | Concatenation Operator(Normally Omitted) |   ab    |       a followed by b        |
|    ()    |           Parenthesis Operator           |   (a)   |  a with operator precedence  |
|    \\    |             Escape Operator              |  \\\*   | '\*' with no special meaning |

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

Run the following command inside the `src` folder :

```
python run_regex_parser.py regex [-w|--word input_word] [-v|--verbose] [-h|--help]
```

**Note** : on some platforms the name of the Python interpreter might be `python3`.<br>
**Note** : at the moment it is assumed that the `regex` passed in is well-formed(i.d. it
respects the formal definition of the operators).

The arguments have the following meanings:

- `regex` : positional argument that specifies the regex(i.d. the pattern to match against).
- `[-w|--word input_word]` : optional argument where `input_word` specifies the word to be tested
  against the regex.
- `[-v|--verbose]` : optional argument that specifies how detailed the output should be.
- `[-h|--help]` : optional argument that describes the purpose of the program and of each argument
  passed to it.

**Note** : in the case of the `regex` and `[-w|--word input_word]` arguments, it is highly
recommended to use double or single quotes, which significantly simplifies the way they are
written, as in the example below :

```
python run_regex_parser.py "(p|a|r|s|e|r)*" -w "parser"
```

## Example of usage

By executing the following command :

```
python run_regex_parser.py "(r|e|g|e|x)*" -w "regex"
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
        Alphabet(4): {'e', 'g', 'r', 'x'}
        Transition Function(25):
                                (0, 'r') --> [1]
                                (2, 'e') --> [3]
                               (3, '_ε') --> [5]
                               (1, '_ε') --> [5]
                               (4, '_ε') --> [2, 0]
                                (6, 'g') --> [7]
                               (7, '_ε') --> [9]
                               (5, '_ε') --> [9]
                               (8, '_ε') --> [6, 4]
                               (10, 'e') --> [11]
                              (11, '_ε') --> [13]
                               (9, '_ε') --> [13]
                              (12, '_ε') --> [10, 8]
                               (14, 'x') --> [15]
                              (15, '_ε') --> [17]
                              (13, '_ε') --> [17]
                              (16, '_ε') --> [14, 12]
                              (17, '_ε') --> [16, 19]
                              (18, '_ε') --> [16, 19]

The word regex matches the regular expression (r|e|g|e|x)*.

```

## Bug Hunting and Future Maintenance

For bugs, logical errors and feature improvements please create a new issue or fork this repository,
make some improvements to the codebase and create a pull request to let me know what you have in mind
:slightly_smiling_face:.
