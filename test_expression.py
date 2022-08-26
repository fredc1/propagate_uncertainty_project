from unittest import TestCase

from expression import Expression


class TestExpression(TestCase):
    def setUp(self) -> None:
        self.blank_expr = Expression("")

    def test_get_variables(self):
        v = self.blank_expr.get_variables()
        self.assertEqual(v, set())
        self.blank_expr.words = {"a", "abc", "b", "c", "cc"}
        v = self.blank_expr.get_variables()
        self.assertEqual(v, {"a", "b", "c"})
        self.blank_expr.words = set([])

    def test_is_safe_to_exec(self):
        self.assertTrue(self.blank_expr._is_safe_to_exec())  # Empty
        self.blank_expr.words = {"for", "sin", "tanh", "a"}  # Illegal words
        self.assertFalse(self.blank_expr._is_safe_to_exec())
        self.blank_expr.words = {"acos", "acosh", "asin", "asinh",  # Maximal Legal Set
                                 "atan", "atanh", "ceil",
                                 "cos", "cosh", "erf", "erfc",
                                 "exp", "fabs", "factorial",
                                 "floor", "gamma", "hypot", "lgamma",
                                 "log", "modf", "pow",
                                 "sin", "sinh", "sqrt", "tan",
                                 "tanh", "trunc", "a", "b", "c"}
        self.assertTrue(self.blank_expr._is_safe_to_exec())
        self.blank_expr.words = set([])

    def test_propagate_uncertainty(self):
        # TODO Make sure that this raises exception of the proper types that will be applicable to the caller
        test_expr = Expression("x+y**2")
        result = test_expr.propagate_uncertainty([("x", 0.0, 0.5), ("y", 3, 0.4)])
        print(result)


class Test(TestCase):
    def test_parse_expr(self):
        r = Expression.parse_expr("a")  # Singleton
        self.assertEqual({"a"}, r)
        r = Expression.parse_expr("")  # Empty
        self.assertEqual(set([]), r)
        r = Expression.parse_expr("sin(x)+b**2/aac")  # Words
        self.assertEqual({"x", "sin", "aac", "b"}, r)
        r = Expression.parse_expr("A+a")  # Upper case
        self.assertEqual({"a", "A"}, r)
        r = Expression.parse_expr("a+a-a/a**a%a")  # Ops + Repeats
        self.assertEqual({"a"}, r)

    def test_str_to_py(self):
        tests = {
            "a+b"}
        self.fail()
