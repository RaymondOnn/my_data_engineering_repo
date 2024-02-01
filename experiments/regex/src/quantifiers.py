from core import RegExp, ensure_regexp_object


class __Quantifier(RegExp):
    def __init__(self, pattern):
        super().__init__(pattern)


class Optional(__Quantifier):
    def __init__(self: RegExp, regexp: RegExp | str, is_greedy: bool = True) -> None:
        super().__init__(ensure_regexp_object(regexp).optional(is_greedy).pattern)


class Maybe(__Quantifier):
    def __init__(self: RegExp, regexp: RegExp | str, is_greedy: bool = True) -> None:
        super().__init__(ensure_regexp_object(regexp).zero_or_more(is_greedy).pattern)


class Some(__Quantifier):
    def __init__(self: RegExp, regexp: RegExp | str, is_greedy: bool = True) -> None:
        super().__init__(ensure_regexp_object(regexp).some(is_greedy).pattern)


class Exactly(__Quantifier):
    def __init__(self: RegExp, regexp: RegExp | str, n: int, is_greedy: bool = True) -> None:
        super().__init__(ensure_regexp_object(regexp).exactly(n, is_greedy).pattern)


class AtLeast(__Quantifier):
    def __init__(self: RegExp, regexp: RegExp | str, n: int, is_greedy: bool = True) -> None:
        super().__init__(ensure_regexp_object(regexp).at_least(n, is_greedy).pattern)


class AtMost(__Quantifier):
    def __init__(self: RegExp, regexp: RegExp | str, n: int, is_greedy: bool = True) -> None:
        super().__init__(ensure_regexp_object(regexp).at_most(n, is_greedy).pattern)


# master class that covers all scenarios
class Quantify(__Quantifier):
    def __init__(self: RegExp, regexp: RegExp | str, n: int, m: int, is_greedy: bool = True) -> None:
        super().__init__(ensure_regexp_object(regexp).quantify(n, m, is_greedy).pattern)
