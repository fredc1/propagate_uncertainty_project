from unittest import TestCase

from expression import Expression


class TestExpression(TestCase):
    def setUp(self) -> None:
        self.blank_expr = Expression("a+b+c")
        self.blank_expr.user_str = ""
        self.blank_expr.words = []
        self.blank_expr.characters = []
        self.blank_expr.expr_str = ""
        self.blank_expr.variables = []

    def test_is_safe_to_exec(self):
        self.blank_expr.words = {"for", "sin", "tanh", "a"}  # Illegal words
        self.assertFalse(self.blank_expr._is_safe_to_exec())
        self.blank_expr.words = {"acos", "acosh", "asin", "asinh",  # Maximal Legal Set
                                 "atan", "atanh", "ceil",
                                 "cos", "cosh", "erf", "erfc",
                                 "exp", "fabs", "factorial",
                                 "floor", "gamma", "lgamma",
                                 "log", "modf",
                                 "sin", "sinh", "sqrt", "tan",
                                 "tanh", "trunc", "a", "b", "c"}
        self.assertTrue(self.blank_expr._is_safe_to_exec())
        self.blank_expr.words = []

    def test_propagate_uncertainty(self):
        test_expr = Expression("x+y^2")
        result = test_expr.propagate_uncertainty([("x", 0.0, 0.5), ("y", 3, 0.4)])
        print(result)

    def test_init(self):
        legal1 = Expression("(a*{b+c})+d")
        legal2 = Expression("29.5678+2^x-10/10+(a)+[b]+{C}*2")

    def test_has_valid_parens(self):
        self.blank_expr.user_str = "(}"
        self.assertFalse(self.blank_expr._has_valid_parens())
        self.blank_expr.user_str = "("
        self.assertFalse(self.blank_expr._has_valid_parens())
        self.blank_expr.user_str = "({[]})"
        self.assertTrue(self.blank_expr._has_valid_parens())
        self.blank_expr.user_str = "(){}[]"
        self.assertTrue(self.blank_expr._has_valid_parens())
        self.blank_expr.user_str = "a+b"
        self.assertTrue(self.blank_expr._has_valid_parens())

    def test_parse_variables(self):
        v = self.blank_expr.get_variables()
        self.assertEqual(v, [])
        self.blank_expr.words = ["a", "abc", "b", "c", "cc"]
        v = self.blank_expr._parse_variables()
        self.assertEqual(v, ["a", "b", "c"])

    def test_parse_expr(self):
        r, c = Expression._parse_expr("a")  # Singleton
        self.assertEqual(["a"], r)
        r, c = Expression._parse_expr("")  # Empty
        self.assertEqual([], r)
        r, c = Expression._parse_expr("sin(x)+b**2/aac")  # Words
        self.assertEqual({"x", "sin", "aac", "b"}, set(r))
        r, c = Expression._parse_expr("A+a")  # Upper case
        self.assertEqual({"a", "A"}, set(r))
        r, c = Expression._parse_expr("a+a-a/a**a%a")  # Ops + Repeats
        self.assertEqual(["a"], r)
