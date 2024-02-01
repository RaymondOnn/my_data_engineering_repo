# Only a small subset of regex features are used:
#   .  wildcard
#   \x escaped literals (for capturing dots or parentheses)
#   () grouping parentheses
#   +  greedy one or more quantifier
#   *  greedy zero or more quantifier
#   ?  zero or one quantifier
# Everything else is considered to be a literal

stack = []
def last(stack)
    return stack[-1]

def parse(expr):
    while i < len(expr) - 1:
        next = expr[i]
        match next:
            case '.':
                stack.append ({
                    'type': 'wildcard',
                    'quantifier': 'exactlyOne'
                })
                i += 1
            case '?':
                lastElement = last(stack)
                if lastElement and lastElement.get('quantifier') != 'exactlyOne':
                    lastElement['quantifier'] = 'zeroOrOne'
                else:
                    print('Quantifier myst follow an unquantigied element or group')
                    i += 1
            case '*':
                lastElement = last(stack)
                if lastElement and lastElement.get('quantifier') != 'exactlyOne':
                  lastElement['quantifier'] = 'zeroOrMore'
                else:
                  print('Quantifier myst follow an unquantigied element or group')
                  i += 1

            case _:
                raise Exception

const last = stack => stack[stack.length-1];
function parse(re) {

  let i = 0;

  while (i < re.length) {
    const next = re[i];

    switch (next) {
      case '.': {
        last(stack).push({
          type: 'wildcard',
          quantifier: 'exactlyOne'
        });
        i++;
        continue;
      }

      case '\\': {
        if (i+1 >= re.length) {
          throw new Error(`Bad escape character at index ${i}`);
        }

        last(stack).push({
          type: 'element',
          value: re[i+1],
          quantifier: 'exactlyOne'
        });

        i += 2;
        continue;
      }

      case '(': {
        stack.push([]);
        i++
        continue;
      }

      case ')': {
        if (stack.length <= 1) {
          throw new Error(`No group to close at index ${i}`);
        }
        const states = stack.pop();
        last(stack).push({
          type: 'groupElement',
          states,
          quantifier: 'exactlyOne'
        });
        i++;
        continue;
      }

      case '?': {
        const lastElement = last(last(stack));
        if (!lastElement || lastElement.quantifier !== 'exactlyOne') {
          throw new Error('Quantifer must follow an unquantified element or group');
        }
        lastElement.quantifier = 'zeroOrOne';
        i++;
        continue;
      }

      case '*': {
        const lastElement = last(last(stack));
        if (!lastElement || lastElement.quantifier !== 'exactlyOne') {
          throw new Error('Quantifer must follow an unquantified element or group');
        }
        lastElement.quantifier = 'zeroOrMore';
        i++;
        continue;
      }

      case '+': {
        const lastElement = last(last(stack));
        if (!lastElement || lastElement.quantifier !== 'exactlyOne') {
          throw new Error('Quantifer must follow an unquantified element or group');
        }

        // Split this into two operations
        // 1. exactly one of the previous quantified element
        // 2. zeroOrMore of the previous quantified element
        const zeroOrMoreCopy = { ...lastElement, quantifier: 'zeroOrMore' };
        last(stack).push(zeroOrMoreCopy);
        i++;
        continue;
      }

      default: {
        last(stack).push({
          type: 'element',
          value: next,
          quantifier: 'exactlyOne'
        });
        i++;
        continue;
      }
    }

  }

  if (stack.length !== 1) {
    throw new Error('Unmatched groups in regular expression');
  }

  return stack[0];
};

module.exports = parse;