from core import RegExp
from classes import *
from quantifiers import *
from groups import Group, BackRef
import re

matches = re.match("\\[(.*?)\\]", '[3-7]')
print(matches.span(), matches.group(0), matches.start(), matches.end(), )
matches_1 = re.findall("\\[(.*?)\\]", '[3-7]')
print(matches_1.)

# http_protocol = Optional('http' + Optional('s') + RegExp('://', escape=True))   # https?://? vs (https?://)?
# print(http_protocol.pattern)
#
# www = Optional('www.')
# print(www)
#
# alphanum = Letter() | Digit()
# print(alphanum)
#
# domain_name = (alphanum + Quantify(alphanum | Char('-', '.', escape=True), n=1, m=61) + alphanum)
# print(domain_name)
#
# tld = '.' + Either('com', 'org')

ip_octet = Digit().quantify(n=1, m=3)
print(3 * (ip_octet + '.'))
# port_number = (Digit() - '0') + 3 * Digit()
# print(port_number)
#
#
# # Combine sub-patterns together.
# pre: RegExp = \
#     http_protocol + \
#     Either(
#         www + Group(domain_name) + tld,
#         3 * (ip_octet + '.') + ip_octet + ':' + port_number
#     )
# print(pre)

'.', '+', '*', '?', '^', '$', '(', ')', '[', ']', '{', '}', '|', '\\'
# '''
# https?://?(www.?([a-zA-Z0-9][a-zA-Z0-9-\.]{1,61}[a-zA-Z0-9])\.(com|org)|[0-9]{1,3}.{3}[0-9]{1,3}:[1-9][0-9]{3})
#
# (https?:\/\/)?
# (
#     (www.)?  ([a-zA-Z0-9][a-zA-Z0-9-\.]{1,61}[a-zA-Z0-9])  \.(com|org)
# |
#    (([0-9]{1,3}\.)  {3})  ([0-9]{1,3})  :  ([1-9][0-9]{3})
# )
#

# - perhaps determine when to escape certain symbol based on class
# - Auto grouping for Either
# - Auto group when multiplying
#
# '''

RegExp('cat').highlight_matches('raining cats and dogs')
