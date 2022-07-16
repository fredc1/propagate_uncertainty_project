from uncertainties.umath import *
from uncertainties import ufloat_fromstr


class Expression:
    permitted_func_strings = {"acos": "Return the arc cosine (measured in radians) of x.",
                              "acosh": "Return the inverse hyperbolic cosine of x.",
                              "asin": "Return the arc sine (measured in radians) of x.",
                              "asinh": "Return the inverse hyperbolic sine of x.",
                              "atan": "Return the arc tangent (measured in radians) of x.",
                              "atanh": "Return the inverse hyperbolic tangent of x.",
                              "ceil": "Return the ceiling of x as an Integral. This is the smallest integer >= x.",
                              "cos": "Return the cosine of x (measured in radians).",
                              "cosh": "Return the hyperbolic cosine of x.",
                              "erf": "Error function at x.",
                              "erfc": "Complementary error function at x.",
                              "exp": "Return e raised to the power of x.",
                              "fabs": "Return the absolute value of the float x.",
                              "factorial": "Find x!. Raise a ValueError if x is negative or non-integral.",
                              "floor": "Return the floor of x as an Integral. This is the largest integer <= x.",
                              "gamma": "Gamma function at x.",
                              "hypot": "Multidimensional Euclidean distance from the origin to a point. Roughly "
                                       "equivalent to: sqrt(sum(x**2 for x in coordinates))",
                              "lgamma": "Natural logarithm of absolute value of Gamma function at x.",
                              "log": "Return the logarithm of x to the given base. If the base not specified, returns the "
                                     "natural logarithm (base e) of x.",
                              "modf": "Return the fractional and integer parts of x. Both results carry the sign of x and "
                                      "are floats.",
                              "pow": "Return x**y (x to the power of y).",
                              "sin": "Return the sine of x (measured in radians).",
                              "sinh": "Return the hyperbolic sine of x.",
                              "sqrt": "Return the square root of x.",
                              "tan": "Return the tangent of x (measured in radians).",
                              "tanh": "Return the hyperbolic tangent of x.",
                              "trunc": "Truncates the Real x to the nearest Integral toward 0."
                              }

    @staticmethod
    def parse_expr(expr) -> set:
        """Returns a list of every contiguous sequence of letters in expr"""
        if len(expr) == 0:
            return set([])
        word = []
        words = []
        for c in (expr + '_'):
            if c.isalpha():
                word.append(c)
            else:
                word_str = "".join(word)
                if word_str != "":
                    words.append(word_str)
                word.clear()
        return set(words)

    @staticmethod
    def get_permitted_function_name_and_desc():
        return Expression.permitted_func_strings

    """Object representation of the expression input by user"""

    def __init__(self, expr_str):
        self.expr_str = expr_str.replace(" ", "")
        self.words = Expression.parse_expr(expr_str)
        if not self.is_safe_to_exec():
            raise ValueError('Illegal words in expression')

    def get_variables(self) -> set:
        """Returns all the variables in the expression."""
        result = []

        for word in self.words:
            if len(word) == 1:
                result.append(word)

        return set(result)

    def is_safe_to_exec(self) -> bool:
        """Must return true before using propagate_uncertainty()

        Ensures that the expression supplied by the user doesn't contain malicious code
        by checking contiguous characters against the list of permitted functions.
        """
        for word in self.words:
            if len(word) > 1 and word not in Expression.permitted_func_strings:
                return False
        return True

    def propagate_uncertainty(self, values) -> str:
        """Returns the value of the expression with uncertainty."""

        result = None
        assignment = "{var_name} = ufloat_fromstr({val_unc})\n"
        command_list = []

        for val in values:
            val_unc_str = f"\"{val[1]}+/-{val[2]}\""
            command_list.append(assignment.format(var_name=val[0], val_unc=val_unc_str))

        command_list.append(f"result = {self.expr_str}\n")
        command = "".join(command_list)
        _locals = locals()
        exec(command, globals(), _locals)

        return _locals["result"].__repr__()
