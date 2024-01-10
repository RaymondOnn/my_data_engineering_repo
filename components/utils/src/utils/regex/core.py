from __future__ import annotations
from typing import Self
# from colorama import Back, Style
import re


# ?: Would the opposite be better i.e. extract pattern
def ensure_regexp_object(regexp: RegExp | str, escape: bool = False):
    if isinstance(regexp, str):
        return RegExp(regexp, escape)
    elif issubclass(regexp.__class__, RegExp):    # <class 'classes.Digit'> <class 'core.RegExp'> True
        return regexp
    else:
        msg = "Pattern must be in the form of a string or an instance of RegExp"
        raise Exception(msg)


class RegExp:
    _pattern = None
    _verbose = True
    _contents = None

    def __init__(self, pattern: RegExp | str = None, escape: bool = False):
        self._input = pattern
        if escape:
            self.literal()

    @property
    def pattern(self):
        if self._pattern is None:
            self._pattern = self._get_pattern()
        return self._pattern

    def _get_pattern(self):
        return self._input

    def _reset_pattern(self):
        self._pattern = None

    # # TODO: Review Again. Not Working
    # def highlight_matches(self, text, print_output=True):
    #     pattern = self._input
    #     output = text
    #     len_inc = 0
    #     for match in pattern.finditer(text):
    #         start, end = match.start() + len_inc, match.end() + len_inc
    #         output = output[:start] + Back.YELLOW + Style.BRIGHT + output[start:end] + Style.RESET_ALL + output[end:]
    #         len_inc = len(output) - len(text)
    #
    #     if print_output:
    #         print(output)
    #     else:
    #         return output

    '''
    Private Methods
    '''

    def __repr__(self):
        class_type = self.__class__.__name__
        match class_type:
            case 'Group':
                return f'{class_type}("{self._contents}")'
            case _:
                return f'{class_type}("{self._input}")'

    def __radd__(self, other):
        # print('radd', self, self._pattern, self._input, other, bool(other))
        if not other:
            return ensure_regexp_object(self._input)
        else:
            if isinstance(other, str):
                other = ensure_regexp_object(other, True)._get_pattern()
            return ensure_regexp_object(other + self._input)

    def __add__(self, other):
        # print('add', self, self.__class__.__name__, self._input, other.__class__.__name__, bool(other))
        # print(issubclass(self.__class__, RegExp), issubclass(other.__class__, RegExp))
        if issubclass(other.__class__, RegExp):
            return self._concat(other, join='left')
        else:
            return ensure_regexp_object(self._input + other)

    def __sub__(self, other):
        return self.xcept(other)

    def __rmul__(self, other):
        # print('rmul', self, self._pattern, self._input, other, bool(other))
        return self.group().exactly(other)

    def __mul__(self, other):
        print('mul', self, self._pattern, self._input, other, bool(other))
        return self.group().exactly(other)

    def __or__(self, other):
        # print("__or__", self, other)
        return self._union(other, join='left')

    def __ior__(self, other):
        print(self, other)
        raise NotImplementedError

    def _is_sequence(self):
        raise NotImplementedError

    @staticmethod
    def _to_sequence(target):
        chars = sorted(list(set([c for c in target])))
        start, stop = min(chars), max(chars)
        seq = [chr(i) for i in range(ord(start), ord(stop) + 1)]

        x, y = 0, 0   # char, seq
        tmp = f'{start}'
        count = 0
        while x <= len(chars) - 1:

            if chars[x] == stop:
                if count == 1:
                    tmp += f'{stop}'
                elif count > 1:
                    tmp += f'-{stop}'
                x += 1
            elif chars[x] == seq[y]:
                count += 1
                x += 1

            else:
                if count == 1:
                    tmp += chars[x]
                elif count > 1:
                    tmp += f'-{chars[x-1]}{chars[x]}'
                count = 0
            y += 1
        return tmp

    @staticmethod
    def _to_char(target: str):
        new_target: str = target
        for outer in re.findall(r"\[(.*?)]", target):
            char_list: list[str] = []
            old_str: str = '[' + outer + ']'
            chars: str = outer
            for inner in re.findall(r"([\d\w])-([\d\w])", outer):
                chars: str = chars.replace("-".join(inner), "")
                start, stop = min(inner), max(inner)
                seq: list[str] = [chr(i) for i in range(ord(start), ord(stop) + 1)]
                char_list += seq

            if char_list:
                chars: list[str] = [c for c in chars]
                seq_final: list[str] = sorted(list(set(char_list + chars)))

                new_str: str = '[' + "".join(seq_final) + "]"
                new_target: str = new_target.replace(old_str, new_str)
        return new_target

    # ?: What if [ (a), \Ac
    def _is_single_char(self, pattern):
        contents, had_brackets = self._remove_brackets(pattern)

        contents = contents[1:] if contents[0] == '^' else contents
        is_one_char = len(contents) == 1
        return any([had_brackets, is_one_char])

    @staticmethod
    def _remove_brackets(pattern) -> tuple[str, bool]:
        matches = re.findall(r"\[(.*?)]", pattern)
        if not matches:  # len(matches) == 0
            return pattern, False
        elif len(matches) == 1:
            return matches[0], True
        else:
            # Assumption: At Most one bracket pair
            raise Exception

    # Test for meta characters e.g. \b
    def _extract_contents(self, pattern: str, symbol: str, escape: bool = False, is_greedy: bool = True):
        if escape:
            symbol = self.literal(symbol)
        regex_str = f'{symbol}(.*?){symbol}{"" if is_greedy else "?"}'
        match_stats = re.match(regex_str, pattern)
        matches = re.findall(regex_str, pattern)
        if matches is None:  # len(matches) == 0
            return {
                'contents': pattern,
                'symbol': symbol,
                'is_enclosed': False,
                'start_pos': None,
                'end_pos': None
            }
        elif len(matches) == 1:
            return {
                'contents': matches[0]
                'symbol': symbol,
                'is_enclosed': True,
                'start_pos': match_stats.start(),
                'end_pos': match_stats.end()
            }
        else:
            # Assumption: At Most one bracket pair
            raise Exception

    # Union: [a] | [b] = [ab]
    def _union(self, regexp: RegExp | str, join: str):
        other = ensure_regexp_object(regexp)
        match join:
            case 'left':
                objects = [self, other]
            case 'right':
                objects = [other, self]
            case _:
                raise Exception

        tmp_str, had_brackets = "", []
        for obj in objects:
            output = self._remove_brackets(obj._input)
            tmp_str += output[0]
            had_brackets.append(output[1])
        if any(had_brackets):
            tmp_str = f'[{tmp_str}]'
        return __class__(tmp_str)

    # Concat: [a] + [b] = [a][b]
    def _concat(self, regexp: RegExp | str, join: str):
        other = ensure_regexp_object(regexp)
        match join:
            case 'left':
                objects = [self, other]
            case 'right':
                objects = [other, self]
            case _:
                raise Exception

        tmp_str = ""
        for obj in objects:
            tmp_str += obj._input
        return __class__(tmp_str)

    '''
    Quantifiers 
    '''

    def optional(self, is_greedy: bool = True) -> Self:
        if self._is_single_char(self._input):
            self._input = f'{self._get_pattern()}?{"" if is_greedy else "?"}'
        else:
            self._input = f'{self.group()._get_pattern()}?{"" if is_greedy else "?"}'
        return self

    def maybe(self, is_greedy: bool = True) -> Self:
        if self._is_single_char(self._input):
            self._input = f'{self._get_pattern()}*{"" if is_greedy else "?"}'
        else:
            self._input = f'{self.group()._get_pattern()}*{"" if is_greedy else "?"}'
        return self

    def some(self, is_greedy: bool = True) -> Self:
        if self._is_single_char(self._input):
            self._input = f'{self._get_pattern()}+{"" if is_greedy else "?"}'
        else:
            self._input = f'{self.group()._get_pattern()}+{"" if is_greedy else "?"}'
        return self

    def at_least(self, n: int, is_greedy: bool = True) -> Self:
        if n == 0:
            return self.maybe(is_greedy)
        if n == 1:
            return self.some(is_greedy)

        if self._is_single_char(self._input):
            self._input = f'{self._get_pattern()}{{{n},}}{"" if is_greedy else "?"}'
        else:
            self._input = f'{self.group()._get_pattern()}{{{n},}}{"" if is_greedy else "?"}'
        return self

    def at_most(self, n: int, is_greedy: bool = True) -> Self:
        if n == 0:
            raise Exception("\"n\" needs to be greater than zero")
        if n == 1:
            return self.optional(is_greedy)

        if self._is_single_char(self._input):
            self._input = f'{self._get_pattern()}{{,{n}}}{"" if is_greedy else "?"}'
        else:
            self._input = f'{self.group()._get_pattern()}{{,{n}}}{"" if is_greedy else "?"}'
        return self

    def exactly(self, n: int, is_greedy: bool = True) -> Self:
        if n == 0:
            raise Exception("\"n\" needs to be greater than zero")

        if self._is_single_char(self._input):
            self._input = f'{self._get_pattern()}{{{n}}}{"" if is_greedy else "?"}'
        else:
            self._input = f'{self.group()._get_pattern()}{{{n}}}{"" if is_greedy else "?"}'
        return self

    def quantify(self, n: int, m: int = None, is_greedy: bool = True) -> Self:
        self._reset_pattern()
        if not any([n, m]):
            raise Exception

        if all([n, m]):
            if n == m:
                return self.exactly(is_greedy)
            if n == 0 and m == 1:
                return self.optional(is_greedy)

            if self._is_single_char(self._input):
                self._input = f'{self._get_pattern()}{{{n},{m}}}{"" if is_greedy else "?"}'
            else:
                self._input = f'{self.group()._get_pattern()}{{{n},{m}}}{"" if is_greedy else "?"}'

        elif n is None:
            return self.at_most(is_greedy)
        elif m is None:
            if n == 0:
                return self.maybe(is_greedy)
            elif n == 1:
                return self.some(is_greedy)
            else:
                return self.at_least(is_greedy)

        return self

    def range(self, start: int | str, stop: int | str):
        self._verbose, start, stop = True, str(start), str(stop)

        # Assumption: Only one "-" character
        front, back = self._input.split('-')[0], self._input.split('-')[-1]
        class_type = self.__class__.__name__
        match class_type:
            case 'Digit':
                self._input = f'{front[:-1]}{start}-{stop}{back[1:]}'
            case 'Lower':
                self._input = f'{front[:-1]}{start.lower()}-{stop.lower()}{back[1:]}'
            case 'Upper':
                self._input = f'{front[:-1]}{start.upper()}-{stop.upper()}{back[1:]}'
            case 'Letter':
                self._input = f'{front[:-1]}{start.lower()}-{stop.lower()}{start.upper()}-{stop.upper()}{back[1:]}'
        return self

    def values(self, *chars):
        self._verbose = True
        self._input = f'[{"".join([str(c) for c in sorted(chars)])}]'
        return self

    # TODO:  What if pattern is [^...]?
    # DEBUG: Use 1 3 4 5 7 9
    def xcept(self, *char):
        output = self._remove_brackets(self._to_char(self._input))
        tmp, had_brackets = output[0], output[1]
        for c in char:
            tmp = tmp.replace(str(c), "")
            self._input = (f'{"[" if had_brackets else ""}'
                           f'{self._to_sequence(tmp)}'
                           f'{"]" if had_brackets else ""}')
        return self

    '''
    Modifiers: Assertions / Either / Literal
    '''

    def match_at_start(self):
        self._input = '^' + self._input
        return self

    def match_at_end(self):
        self._input = '$'
        return self

    # look ahead
    def before(self, regexp: RegExp | str,  is_negated: bool = False):
        lookahead_pattern = ensure_regexp_object(regexp).pattern
        self._input = f'{self._get_pattern()}(?{"!" if is_negated else "="}{lookahead_pattern})'
        return self

    def after(self, regexp: RegExp | str,  is_negated: bool = False):
        lookbehind_pattern = ensure_regexp_object(regexp).pattern
        self._input = f'{self._get_pattern()}(?<{"!" if is_negated else "="}{lookbehind_pattern})'
        return self

    # def either(self) -> Self:
    #
    #     if len(re.findall(r"\[(.*?)]", self._to_char(self._input))) == 1
    #         target =
    #     return self

    def exclude(self):
        tmp, had_brackets = self._remove_brackets(self._input)
        self._input = f'{"[" if had_brackets else ""}^{tmp}{"]" if had_brackets else ""}'
        return self

    # TODO: Has Bugs
    # Exclude(Digit().values("2")): [*2\] -> Brackets gets wrongly escaped
    # What if Quantifiers are included in the pattern
    def literal(self):
        special_char = ['.', '+', '*', '?', '^', '$', '(', ')', '[', ']', '{', '}', '|', '\\']
        new_str = ""
        for c in self._input:
            if c in special_char:
                new_str += c.replace(c, f'\\{c}')
            else:
                new_str += c
        self._input = new_str
        return self

    '''
    Groups / Back References
    '''

    def group(self, name: str = None, capture: bool = True):
        self._reset_pattern()
        n = "?P<" + name + ">" if name else ""
        self._input = f'({"?:" if not capture else ""}{n if n else ""}{self._input})'
        return self
