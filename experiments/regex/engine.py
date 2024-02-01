def is_start(char):
    return char == '^'

def is_end(char):
    return char == '$'

def is_star(char):
    return char == "*"


def is_plus(char):
    return char == '+'


def is_question(char):
    return char == '?'

def is_quantifier(char):
    return is_star(char) or is_plus(char) or is_question(char)

def is_dot(char):
    return char == '.'

def is_escape(char):
    return char == "\\"

def is_escape_sequence(term):
    return is_escape(term[0])
def is_literal(char):
    return char.isalpha() or char.isdigit() or char in list(' :/')

def is_open_alternate(char):
    return char == "("

def is_close_alternate(char):
    return char == ")"

def is_alternate(term):
    return is_open_alternate(term[0]) and is_close_alternate(term[-1])
def is_set(term):
    return is_open_set(term[0]) and is_close_set(term[-1])

def is_unit(term):
    return (is_literal(term[0])     # e.g. a
            or is_dot(term[0])      # e.g. .
            or is_set(term)         # e.g. [123]
            or is_escape_sequence(term)   # e.g. \d
            )
def is_open_set(char):
    return char == '['

def is_close_set(char):
    return char == ']'

def split_set(set_head):
    set_inside = set_head[1:-1]
    set_terms = list(set_inside)
    return set_terms

def split_alternate(alternate):
    return alternate[1:-1].split("|")
def split_expr(expr):
    head, quantifier, rest = None, None, None
    last_expr_pos = 0

    # e.g.
    if is_open_set(expr[0]):
        last_expr_pos = expr.find(']') + 1
        head = expr[:last_expr_pos]     # e.g. extract [123] from [123]*abc
    elif is_open_alternate(expr[0]):
        last_expr_pos = expr.find(')') + 1
        head = expr[:last_expr_pos]     # e.g. extract (123) from (123)*abc
    elif is_escape(expr[0]):
        last_expr_pos += 2
        head = expr[:2]
    else:   #  is_literal(expr[0]):
        last_expr_pos = 1
        head = expr[0]                  # e.g. extract a from a*bc


    if last_expr_pos < len(expr) and is_quantifier(expr[last_expr_pos]):
        quantifier = expr[last_expr_pos]  # extract * from *abc
        last_expr_pos += 1

    rest = expr[last_expr_pos:]
    return head, quantifier, rest

def does_unit_match(expr, string):
    '''determines whether there is a match '''
    if len(string) == 0:
        return False

    head, quantifier, rest = split_expr(expr)
    if is_literal(head):
        return expr[0] == string[0]
    elif is_dot(head):
        return True
    elif is_escape_sequence(head):
        if head == '\\a':
            return string[0].isalpha()
        elif head == '\\d':
            return string[0].isdigit()
        else:
            return False
    elif is_set(head):
        set_terms = split_set(head)
        return string[0] in set_terms
    return False

def match_multiple(expr, string, match_length, min_match_length = None, max_match_length = None):
    head, quantifier, rest = split_expr(expr)

    if not min_match_length:
        min_match_length = 0

    submatch_length = - 1

    while not max_match_length or (submatch_length < max_match_length):
        subexpr_matched, subexpr_length = match_expr((head * (submatch_length + 1)), string, match_length)
        if subexpr_matched:
            submatch_length += 1
        else:
            break

    while submatch_length >= min_match_length:
        matched, new_match_length = match_expr((head * submatch_length) + rest, string, match_length)
        if matched:
            return [matched, new_match_length]
        submatch_length -= 1
    return [False, None]

def match_star(expr, string, match_length):
    return match_multiple(expr, string, match_length, None, None)

def match_plus(expr, string, match_length):
    return match_multiple(expr, string, match_length, 1, None)

def match_question(expr, string, match_length):
    return match_multiple(expr, string, match_length, 0, 1)

def match_alternate(expr, string, match_length):
    head, quantifier, rest = split_expr(expr)
    options = split_alternate(head)

    for option in options:
        matched, new_match_length = match_expr(option + rest, string, match_length)
        if matched:
            return [matched, new_match_length]
    return [False, None]

def match_expr(expr, string,  match_length: int = 0):
    if len(expr) == 0:  # when fully matched
        return [True, match_length]
    elif is_end(expr[0]):
        if len(string) == 0:  # if there's no more string left, i.e. we've reached the end
            return [True, match_length]
        else: # if is_end but there is still string to match
            return [False, None]

    head, quantifier, rest = split_expr(expr)
    if is_star(quantifier):
        return match_star(expr, string, match_length)
    elif is_plus(quantifier):
        return match_plus(expr, string, match_length)
    elif is_question(quantifier):
        return match_question(expr, string, match_length)
    elif is_alternate(head):
        return match_alternate(expr, string, match_length)
    elif is_unit(head):
        if does_unit_match(expr, string):
            # print(expr, string, match_length)
            return match_expr(rest, string[1:], match_length + 1)  # move on to next char and repeat match_expr
    else:
        print(f'Unknown token expr: {expr}')
    return [False, None] # does not match since cannot fully match


# recursively apply match_expr() for the entire string
def match(expr, string):
    match_pos, matched = 0, False,
    if is_start(expr[0]):
        last_match_pos = 0
        expr = expr[1:]    # remove the '^' symbol
    else:
        last_match_pos = len(string) - 1

    while not matched and match_pos <= last_match_pos:
        [matched, match_length] = match_expr(expr, string[match_pos:])
        if matched: # haven;t found anything that fully matches
            return [matched, match_pos, match_length]    # exit function
        match_pos += 1
    return [False, None, None]

def main():

    cases = [
        ('a*bc', 'Hello abc how'),
        ('[Hh][Ee]llo', 'HEllo'),
        ('[abc].[123]', 'the code is bw2'),
        ('ab*c', 'abbbc'),
        ('1(cat|dog)2', '1cat2'),
        ('I am a (cat|do?g)+', 'Hello I am a dogdg'),
        ('^abc', '123abc'),
        ('abc$', '123abc'),
        ('.com$', r'http://www.google.com'),
        ('(\\a|\\d)+', r'regex101'),

    ]

    for case in cases:
        expr, string = case
        [matched, match_pos, match_length] = match(expr, string)
        if matched:
            result = string[match_pos:match_pos + match_length]
            print(f'match_expr({expr}, {string}) = {result}')
        else:
            print(f'match_expr({expr}, {string}) = False')


# missing features:
# quantifiers: {n}, {n,}, {,n}, [n,m]
# negation: [^a]
# greedy: {n,m}?
# lookaheads / lookbehind:
# meta characters: \b
# group - non_capture, name, backreference



if __name__ == '__main__':
    main()
