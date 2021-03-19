"""
Here's where the money's made baby
"""

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
    """
    Models either a dice roll or constant modifier
    """
    def value(self):
        """Returns value of component"""

    def results(self):
        """Gets raw value of component"""

    @staticmethod
    def from_expr(expr: str):
        """Factory method that takes a roll expression"""
        res = None
        if re.match(DIE_EXPR, expr[1:]):
            res = DiceRoll.from_expr(expr)
        elif re.match(MOD_EXPR, expr[1:]):
            res = Modifier.from_expr(expr)
        return res


class DiceRoll(RollComponent):
    """Models a roll component"""
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

    @staticmethod
    def from_expr(expr: str):
        negative = expr[0] == '-'
        expr = expr[1:]

        num, sides = map(int, expr.split('d'))
        return DiceRoll(num, sides, negative)


class Modifier(RollComponent):
    """Models constant modifiers"""
    def __init__(self, val: int):
        self.val = val

    def results(self):
        return self.val

    def value(self):
        return self.val

    @staticmethod
    def from_expr(expr: str):
        """Factory method that takes a modifier expression"""
        return Modifier(int(expr))


class Transform():
    """Models result transforms"""
    def apply(self, comp: RollComponent):
        """Applies transform"""

    @staticmethod
    def from_expr(expr: str):
        """Factory method that takes a transform expression"""
        res = None
        if re.match(KH_EXPR, expr):
            res = KeepHighestTransform.from_expr(expr)
        elif re.match(KL_EXPR, expr):
            res = KeepLowestTransform.from_expr(expr)
        return res


class KeepHighestTransform(Transform):
    """Keeps maximum values in roll"""
    def __init__(self, num):
        self._num = num

    def apply(self, comp: RollComponent):
        """Applies transform"""
        if isinstance(comp, list):
            return sorted(comp, reverse=True)[:self._num]
        return comp

    @staticmethod
    def from_expr(expr: str):
        return KeepHighestTransform(int(expr[2:]))


class KeepLowestTransform(Transform):
    """Keeps minimum values in roll"""
    def __init__(self, num):
        self._num = num

    def apply(self, comp: RollComponent):
        """Applies transform"""
        if isinstance(comp, list):
            return sorted(comp)[:self._num]
        return comp

    @staticmethod
    def from_expr(expr: str):
        return KeepLowestTransform(int(expr[2:]))


class Roll():
    """Models entire roll"""
    def __init__(
        self,
        roll_comps,
        xforms=None,
    ):
        self._roll_comps = roll_comps
        self._xforms = xforms or []
        self._results = []
        self._total = 0
        self._roll()

    @staticmethod
    def from_expr(expr: str):
        """Factory method that takes roll expression"""
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
            xforms = list(map(Transform.from_expr, xform_tokens))
        else:
            roll_clause = '+' + expr.strip().replace(' ', '')

        tokens = re.findall(POS_ROLL_COMP_EXPR, roll_clause)
        roll_comps = list(map(RollComponent.from_expr, tokens))

        return Roll(roll_comps, xforms)

    def _roll(self):
        for roll_comp in self._roll_comps:
            result = roll_comp.results()
            for xform in self._xforms:
                result = xform.apply(result)
            if isinstance(result, list):
                self._results.append(sorted(result))
                self._total += sum(result)
            else:
                self._results.append(result)
                self._total += result

    def get(self):
        """Gets rol result"""
        return (self._results, self._total)
