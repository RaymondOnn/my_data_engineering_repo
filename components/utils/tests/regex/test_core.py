



def debug_lazy_attr(how, cls):
    part_1 = cls("a")
    print(f"* {how} First time of retrieving the pattern")
    print(part_1.pattern)
    print(f"* {how} Second time of retrieving the pattern")
    print(part_1.pattern)

debug_lazy_attr("property", RegExp)