from uncertainties.umath import *
from uncertainties import ufloat_fromstr


class Expression:
    permitted_func_strings = {"acos": ("acos(x)", "Return the arc cosine (measured in radians) of x."),
                              "acosh": ("acosh(x)", "Return the inverse hyperbolic cosine of x."),
                              "asin": ("asin(x)", "Return the arc sine (measured in radians) of x."),
                              "asinh": ("asinh(x)", "Return the inverse hyperbolic sine of x."),
                              "atan": ("atan(x)", "Return the arc tangent (measured in radians) of x."),
                              "atanh": ("atanh(x)", "Return the inverse hyperbolic tangent of x."),
                              "ceil": ("ceil(x)", "Return the ceiling of x as an Integral. This is the smallest "
                                                  "integer >= x."),
                              "cos": ("cos(x)", "Return the cosine of x (measured in radians)."),
                              "cosh": ("cosh(x)", "Return the hyperbolic cosine of x."),
                              "erf": ("erf(x)", "Error function at x."),
                              "erfc": ("erfc(x)", "Complementary error function at x."),
                              "exp": ("exp(x)", "Return e raised to the power of x."),
                              "fabs": ("fabs(x)", "Return the absolute value of the float x."),
                              "factorial": ("factorial(x)", "Find x!. Raise a ValueError if x is negative or "
                                                            "non-integral."),
                              "floor": ("floor(x)", "Return the floor of x as an Integral. This is the largest integer "
                                                    "<= x."),
                              "gamma": ("gamma(x)", "Gamma function at x."),
                              "lgamma": ("lgamma(x)", "Natural logarithm of absolute value of Gamma function at x."),
                              "log": ("log(x, b)", "Return the logarithm of x to the base b. If the base not "
                                                   "specified, returns the natural logarithm (base e) of x."),
                              "modf": ("modf(x)", "Return the fractional and integer parts of x. Both results carry "
                                                  "the sign of x and are floats."),
                              "sin": ("sin(x)", "Return the sine of x (measured in radians)."),
                              "sinh": ("sinh(x)", "Return the hyperbolic sine of x."),
                              "sqrt": ("sqrt(x)", "Return the square root of x."),
                              "tan": ("tan(x)", "Return the tangent of x (measured in radians)."),
                              "tanh": ("tanh(x)", "Return the hyperbolic tangent of x."),
                              "trunc": ("trunc(x)", "Truncates the Real x to the nearest Integral toward 0.")
                              }
    permitted_operator_strings = ['+', '-', '/', '*', '^', '(', ')', '[', ']', '{', '}']

    def __init__(self, expr_str):
        """Object representation of the expression input by user"""
        self.user_str = expr_str.replace(" ", "")
        self.words, self.characters = Expression._parse_expr(expr_str)
        self.variables = self._parse_variables()
        if not self._is_safe_to_exec():
            raise ValueError('Illegal words in expression, check legal function list')
        if not self._has_legal_operators():
            raise ValueError('Illegal characters in expression, check legal operator list')
        if not self._has_valid_parens():
            raise ValueError('Invalid parenthesis in expression')
        self.expr_str = self.user_str.replace("[", "(").replace("]", ")").replace("{", "(").replace("}", ")").replace(
            "^", "**")
        if len(self.variables) > 200:
            raise ValueError("Too many variables in expression")
        values = []
        for var in self.variables:
            values.append((var, "0", "0"))
        try:
            self.propagate_uncertainty(values)
        except Exception as e:
            raise ValueError('There is something wrong with the input expression')

    @staticmethod
    def get_permitted_expression_functions():
        return Expression.permitted_func_strings

    @staticmethod
    def get_permitted_expression_operators():
        return Expression.permitted_operator_strings

    def propagate_uncertainty(self, values) -> str:
        """Returns the value of the expression with uncertainty."""

        result = None
        assignment = "{var_name} = ufloat_fromstr({val_unc})\n"
        command_list = []

        for val in values:
            val_unc_str = f"\"{val[1]}+/-{val[2]}\""
            command_list.append(assignment.format(var_name=val[0], val_unc=val_unc_str))

        command_list.append(f"result = {self.user_str}\n")
        command = "".join(command_list)
        _locals = locals()
        exec(command, globals(), _locals)

        return _locals["result"].__repr__()

    def get_variables(self) -> set:
        """Returns all the variables in the expression."""
        return self.variables

    def _is_safe_to_exec(self) -> bool:
        """Must return true before using propagate_uncertainty()

        Ensures that the expression supplied by the user doesn't contain malicious code
        by checking contiguous characters against the list of permitted functions.
        """
        for word in self.words:
            if len(word) > 1 and word not in Expression.permitted_func_strings:
                return False
        return True

    @staticmethod
    def _parse_expr(expr):
        """Returns a list of every unique contiguous sequence of letters in expr and every unique character"""
        if len(expr) == 0:
            return set([])
        word = []
        words = []
        characters = []
        for c in (expr + '_'):
            if c not in characters and c != '_':
                characters.append(c)
            if c.isalpha():
                word.append(c)
            else:
                word_str = "".join(word)
                if word_str != "":
                    if word not in words:
                        words.append(word_str)
                word.clear()
        return words, characters

    def _parse_variables(self):
        result = []

        for word in self.words:
            if len(word) == 1:
                if word not in result:
                    result.append(word)

        return result

    def _has_legal_operators(self):
        for c in Expression.permitted_operator_strings:
            assert not c.isalpha()

        for c in self.characters:
            if (not c.isalpha()) and (c not in Expression.permitted_operator_strings):
                print(f"failing var: {c}")
                return False
        return True

    def _has_valid_parens(self):
        stack = []
        s = self.user_str

        mapping = {")": "(", "}": "{", "]": "["}
        for char in s:
            if char in mapping:
                top_element = stack.pop() if stack else '#'
                if mapping[char] != top_element:
                    return False
            elif (not char.isalpha()) and (char not in Expression.permitted_operator_strings):
                stack.append(char)

        return not stack
