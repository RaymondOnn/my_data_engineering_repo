from core import RegExp, ensure_regexp_object
import re


class __Group(RegExp):
    def __init__(self, pattern):
        super().__init__(pattern)

    def _get_groups(self):
        raise NotImplementedError


class Group(__Group):
    def __init__(self, regexp: RegExp | str, name: str = None, capture: bool = True):
        regexp_obj = ensure_regexp_object(regexp)
        self._contents = regexp_obj.pattern
        super().__init__(regexp_obj.group(name, capture).pattern)

    @property
    def contents(self):
        return self._contents


class BackRef(__Group):
    def __init__(self, name: str = None, index: int | str = None):
        if not any([name, index]):
            raise Exception  # A reference, either by name or index, is required

        # back ref by name; will trigger if both are True as well
        if name and isinstance(name, str):
            if re.fullmatch("[A-Za-z_][A-Za-z_0-9]*", name) is None:
                raise Exception  # InvalidGroupNameException(name)
            else:
                pattern = f'(?P={name})'

        # back ref by index
        elif index:
            print(index, int(index))
            if not int(index) in range(1, 100):
                raise Exception    # InvalidArg: Index must be a non-zero integer between 1 and 99
            else:
                pattern = f'\\{index}'
        else:
            raise Exception  # Parameter is neither a string nor an integer
        super().__init__(pattern)
