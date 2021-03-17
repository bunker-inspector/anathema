import random
import re

POS_EXPR = r'[\+|\-]'
DIE_EXPR = r'\d+[d]\d+'
MOD_EXPR = r'\d+'
ROLL_COMP_EXPR = r'({}|{})'.format(DIE_EXPR, MOD_EXPR)
ROLL_COMPS_EXPR = r'(\s*{}\s*{})*'.format(POS_EXPR, ROLL_COMP_EXPR)
POS_ROLL_COMP_EXPR = r'{}{}|{}{}'.format(POS_EXPR, DIE_EXPR, POS_EXPR,
                                         MOD_EXPR)

KH_EXPR = r'kh\d+'
KL_EXPR = r'kl\d+'

XFORM_EXPRS = [KH_EXPR, KL_EXPR]

XFORM_EXPR = r'({})'.format('|'.join(XFORM_EXPRS))
ROLL_EXPR = r'{}{}(\s+{}\s*)*'.format(ROLL_COMP_EXPR, ROLL_COMPS_EXPR,
                                      XFORM_EXPR)


class RollComponent():
    def value(self):
        return None

    def results(self):
        return None

    def from_expr(expr: str):
        if re.match(DIE_EXPR, expr[1:]):
            return DiceRoll.from_expr(expr)
        elif re.match(MOD_EXPR, expr[1:]):
            return Modifier.from_expr(expr)


class DiceRoll(RollComponent):
    def __init__(self, num: int, sides: int, negative=False):
        self._num = num
        self._sides = sides
        self._negative = negative
        self._results = []
        self._roll()

    def _roll(self):
        for _ in range(self._num):
            res = random.randint(1, self._sides)
            if self._negative:
                res = -res

            self._results.append(res)

    def results(self):
        return self._results

    def from_expr(expr: str):
        negative = expr[0] == '-'
        expr = expr[1:]

        num, sides = map(int, expr.split('d'))
        return DiceRoll(num, sides, negative)


class Modifier(RollComponent):
    def __init__(self, v: int):
        self.v = v

    def results(self):
        return self.v

    def value(self):
        return self.v

    def from_expr(expr: str):
        return Modifier(int(expr))


class Transform():
    def apply(self, pre_results):
        pass

    def from_expr(expr: str):
        if re.match(KH_EXPR, expr):
            return KeepHighestTransform.from_expr(expr)
        elif re.match(KL_EXPR, expr):
            return KeepLowestTransform.from_expr(expr)


class KeepHighestTransform(Transform):
    def __init__(self, num):
        self._num = num

    def apply(self, x: RollComponent):
        if type(x) is list:
            return sorted(x, reverse=True)[:self._num]
        else:
            return x

    def from_expr(expr: str):
        return KeepHighestTransform(int(expr[2:]))


class KeepLowestTransform(Transform):
    def __init__(self, num):
        self._num = num

    def apply(self, x: RollComponent):
        if type(x) is list:
            return sorted(x)[:self._num]
        else:
            return x

    def from_expr(expr: str):
        return KeepLowestTransform(int(expr[2:]))


class Roll():
    def __init__(
        self,
        roll_comps,
        xforms=[],
    ):
        self._roll_comps = roll_comps
        self._xforms = xforms
        self._results = []
        self._total = 0
        self._roll()

    def from_expr(expr: str):
        expr = expr.strip()

        if not re.fullmatch(ROLL_EXPR, expr):
            return None

        roll_clause = '+' + expr
        xforms = []
        match = re.search(XFORM_EXPR, expr)
        if match:
            split_idx = match.start()
            roll_clause = '+' + expr[:split_idx].strip().replace(' ', '')
            xform_tokens = expr[split_idx:].strip().split()
            xforms = [x for x in map(Transform.from_expr, xform_tokens)]
        else:
            roll_clause = '+' + expr.strip().replace(' ', '')

        tokens = re.findall(POS_ROLL_COMP_EXPR, roll_clause)
        roll_comps = [x for x in map(RollComponent.from_expr, tokens)]

        return Roll(roll_comps, xforms)

    def _roll(self):
        for roll_comp in self._roll_comps:
            result = roll_comp.results()
            for xform in self._xforms:
                result = xform.apply(result)
            if type(result) is list:
                self._results.append(sorted(result))
                self._total += sum(result)
            else:
                self._results.append(result)
                self._total += result

    def get(self):
        return (self._results, self._total)
