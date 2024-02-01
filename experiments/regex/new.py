from pprint import pprint

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


def is_open_alternate(char):
    return char == "("

def is_close_alternate(char):
    return char == ")"

def is_alternate(term):
    return is_open_alternate(term[0]) and is_close_alternate(term[-1])

def is_either(term):
    return is_alternate(term) and "|" in term
def is_open_set(char):
    return char == '['

def is_close_set(char):
    return char == ']'

def is_set(term):
    return is_open_set(term[0]) and is_close_set(term[-1])
def is_literal(char):
    return char.isalpha() or char.isdigit() or char in list(' :/')

def split_alternate(alternate):
    return alternate[1:-1].split("|")

def split_expr(expr):
    head, quantifier, rest = None, None, None
    last_expr_pos = len(expr) - 1

    if is_open_set(expr[0]):
        last_expr_pos = expr.find(']') + 1
        head = expr[:last_expr_pos]     # e.g. extract [123] from [123]*abc
    elif is_open_alternate(expr[0]):
        last_expr_pos = expr.find(')') + 1
        head = expr[:last_expr_pos]     # e.g. extract (123) from (123)*abc
    else:
        last_expr_pos = 1
        head = expr[0]


    if last_expr_pos < len(expr) and is_quantifier(expr[last_expr_pos]):
        quantifier = expr[last_expr_pos]  # extract * from *abc
        last_expr_pos += 1

    rest = expr[last_expr_pos:]
    return head, quantifier, rest

def infer_type(head, quantifier):
    head_type, quantifier_type = None, None

    if is_dot(head):
        head_type = 'wildcard'
    elif is_set(head):
        head_type = 'set'
    elif is_either(head):
        head_type = 'either'
    elif is_alternate(head):
        head_type = 'group'
    elif is_literal(head):
        head_type = 'literal'
    else:
        print(f'Unknown token: {head}')

    quantifier_dict = {
        '?': 'optional',
        '+': 'one_or_more',
        '*': 'zero_or_more'
    }
    if quantifier is not None:
        if quantifier in quantifier_dict.keys():
            quantifier_type = quantifier_dict.get(quantifier)
        else:
            print(f'Unknown quantifier: {quantifier}')
    return head_type, quantifier_type

def consolidate_types(types):
    # Assumption: Keys only type, value, quantifier
    new_types = []
    tmp = types[0]


    for i in range(1, len(types)):
        if is_set(tmp.get('value')):
            new_types.append(tmp)
            tmp = types[i]
        elif tmp.get('quantifier') == types[i].get('quantifier') and tmp.get('type') == types[i].get('type'):
            tmp['value'] = tmp.get('value') + types[i].get('value')
        else:
            new_types.append(tmp)
            tmp = types[i]
    new_types.append(tmp)
    return new_types


def analyze_expr(expr, types:list = None):
    if len(expr) == 0:
        raise Exception("No expression provided for analysis")

    array = types if types else []
    head, quantifier, rest = split_expr(expr)  # a _ bc
    head_type, quantifier_type = infer_type(head, quantifier)

    if is_either(head):
        for option in split_alternate(head):
            stack = analyze_expr(option)
            array.append({
                'type': head_type,
                'value': stack,
                'quantifier': quantifier_type
            })
    if is_alternate(head):
        for option in split_alternate(head):
            stack = analyze_expr(option)
            array.append({
                'type': head_type,
                'value': stack,
                'quantifier': quantifier_type
            })
    else:
        array.append({
            'type': head_type,
            'value': head,
            'quantifier': quantifier_type
        })
    if rest:
        return analyze_expr(rest, array)
    else:
        return array


def consolidate_types(types):
    # Assumption: Keys only type, value, quantifier
    new_types = []
    tmp = types[0]
    i = 1

    while True:
        if is_set(tmp.get('value')):
            new_types.append(tmp)
            tmp = types[i]
        elif tmp.get('quantifier') == types[i].get('quantifier') and tmp.get('type') == types[i].get('type'):
            tmp['value'] = tmp.get('value') + types[i].get('value')
        else:
            new_types.append(tmp)
            tmp = types[i]
    new_types.append(tmp)
    return new_types
def analyze(expr):
    types = analyze_expr(expr)
    return consolidate_types(types)

def main():
    cases = [
     #   '.+',
     #   'ab?c',
     #   '[Hh][Ee]llo',
     #   '[abc].[123]',
     #   '1(cat|dog)2',
        '(abc)?'
    ]
    for case in cases:
        pprint(analyze(case))

if __name__ == '__main__':
    main()



