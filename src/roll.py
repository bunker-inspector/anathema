import random
import re

POS_EXPR = r'[\+|\-]+'
DIE_EXPR = r'\d+[d]\d+'
MOD_EXPR = r'\d+(?!(d|\d+d))'
ROLL_COMP_EXPR = r'({}|{})'.format(DIE_EXPR, MOD_EXPR)
ROLL_COMPS_EXPR = r'({}{})*'.format(POS_EXPR, ROLL_COMP_EXPR)

KH_EXPR = r'kh\d+'
KL_EXPR = r'kl\d+'

XFORM_EXPRS = [KH_EXPR, KL_EXPR]

XFORM_EXPR = r'({})'.format('|'.join(XFORM_EXPRS))
ROLL_EXPR = r'{}{}(\s+({}*))?'.format(ROLL_COMP_EXPR, ROLL_COMPS_EXPR,
                                      XFORM_EXPR)


class RollComponent():
    def value(self):
        return None

    def from_expr(expr: str):
        if re.match(DIE_EXPR, expr):
            return DiceRoll.from_expr(expr)
        elif re.match(MOD_EXPR, expr):
            return Modifier.from_expr(expr)


class DiceRoll(RollComponent):
    def __init__(self, num: int, sides: int):
        self._num = num
        self._sides = sides
        self._results = []
        self._total = 0
        self._roll()

    def roll(self):
        for _ in range(self._num):
            res = random.randint(1, self._sides)
            self._results.append(res)
            self._total += res

    def from_expr(expr: str):
        num, sides = map(int, expr.split('d'))
        return DiceRoll(num, sides)


class Modifier(RollComponent):
    def __init__(self, v: int):
        self.v = v

    def value(self):
        return self.v

    def from_expr(expr: str):
        return int(expr)


class Roll():
    def __init__(
        self,
        rolls,
        mods,
    ):
        pass

    def from_expr(expr: str):
        if not re.fullmatch(ROLL_EXPR, expr):
            return None

        return "Yoooo"

    def _parse_xforms(expr: str) -> [re.Match]:
        return re.findall(XFORM_EXPR, expr)

    def _roll(self, roll):

        return [random.randint(1, die) for _ in range(times)]

    def _apply_xforms(self, roll_results, xform_tokens):
        for token in xform_tokens:
            if re.fullmatch(KH_EXPR, token):
                take = int(token[2:])
                roll_results = map(lambda x: sorted(x)[-take:], roll_results)
            elif re.fullmatch(KL_EXPR, token):
                take = int(token[2:])
                roll_results = map(lambda x: sorted(x)[:take], roll_results)

        return [x for x in roll_results]
