# Simple Regex Parser

The purpose of this project is to provide a basic implementation of a regex parser.

# Supported Operators

The following are the operators that are recognized by the parser :

| Symbol |          Formal Name         | Example |         Description        |
|  :---: |             :---:            |  :---:  |            :--:            |
|    *   | Kleene Operator(Kleene Star) |    a*   | 0 or more occurrences of a |
|   \|   | Alternation Operator(Union)  |   a\|b  |          a or b            |
|    .   |    Concatenation Operator    |    ab   |      a followed by b       |
|   ()   |     Parenthesis Operator     |   (a)   | a with operator precedence |

# Supported Alphabet Symbols

The parser **should** accept all possible characters except for the "ε" character and eventual spaces.
