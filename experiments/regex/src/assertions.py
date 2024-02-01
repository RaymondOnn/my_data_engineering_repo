from core import RegExp, ensure_regexp_object


class __Assertion(RegExp):
    def __init__(self, pattern):
        super().__init__(pattern)


class After(__Assertion):
    def __init__(self, regexp: RegExp | str, ref_pattern: RegExp | str, is_negated) -> None:
        super().__init__(ensure_regexp_object(regexp).after(ref_pattern, is_negated).pattern)


class Before(__Assertion):
    def __init__(self, regexp: RegExp | str, ref_pattern: RegExp | str, is_negated) -> None:
        super().__init__(ensure_regexp_object(regexp).before(ref_pattern, is_negated).pattern)


# TODO: Check Again
class Between(__Assertion):
    # After + Before
    def __init__(self, after: RegExp | str, before: RegExp | str, negate_after: bool, negate_before: bool):
        super().__init__(ensure_regexp_object(regexp).after(after, negate_after).before(before, negate_before).pattern)


class MatchAtStart(__Assertion):
    def __init__(self, regexp: RegExp | str) -> None:
        super().__init__(ensure_regexp_object(regexp).match_at_start().pattern)


class MatchAtEnd(__Assertion):
    def __init__(self, regexp: RegExp | str) -> None:
        super().__init__(ensure_regexp_object(regexp).match_at_end().pattern)


class WordBoundary(__Assertion):
    def __init__(self):
        super().__init__(r'\b')
