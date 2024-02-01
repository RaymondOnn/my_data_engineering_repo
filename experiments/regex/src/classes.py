from core import RegExp, ensure_regexp_object

ANY_CHAR = RegExp('.')
ANYTHING = ""
SOMETHING = ""
EVERYTHING = ""


class __Class(RegExp):
    is_negated = False

    def __init__(self, pattern: str, is_negated: bool = False, verbose: bool = True):
        self.is_negated, self._verbose = is_negated, verbose
        super().__init__(pattern)

    def negate(self):
        # self.is_negated = True

        if self._verbose:
            self._input = self._input.replace('[', '[^')
        else:
            self._input = self._input.upper()
        return self


class Digit(__Class):
    def __init__(self, pattern: str = None, verbose: bool = True):
        if pattern is None:
            if verbose:
                pattern = r'[0-9]'
            else:
                pattern = r'\d'
        super().__init__(pattern, verbose)


class Space(__Class):
    def __init__(self):
        super().__init__(r'\s', verbose=False)


# TODO: \w includes underscore "_"
class Letter(__Class):
    def __init__(self, verbose: bool = True):
        if verbose:
            super().__init__(r'[a-zA-Z]')
        else:
            super().__init__(r'\w')


class Upper(__Class):
    def __init__(self):
        super().__init__(r'[A-Z]')


class Lower(__Class):
    def __init__(self):
        super().__init__(r'[a-z]')


class Char(__Class):
    def __init__(self, *regexp, escape: bool = False):
        super().__init__(''.join([ensure_regexp_object(item, escape).pattern for item in regexp]))


class Either(__Class):
    def __init__(self, *regexp: RegExp | str) -> None:
        super().__init__('(' + '|'.join([ensure_regexp_object(item).pattern for item in regexp]) + ')')


class Exclude(__Class):
    def __init__(self, regexp: RegExp | str, escape: bool = False) -> None:
        super().__init__(ensure_regexp_object(regexp, escape).exclude().pattern)


DIGIT = Digit()
LETTER = __Class(r'[a-zA-Z]')
ANYCHAR = __Class(r'.')
# ANYTHING = __Class()
# EVERYTHING = __Class()
# ANYTHING = __Class()
# PUNCTUATION = __Class()
