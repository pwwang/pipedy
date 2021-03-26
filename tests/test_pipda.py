from types import FunctionType
from typing import Any, Type
import unittest
from pipda import *

class TestCase(unittest.TestCase):

    def test_case(self):
        X = Symbolic()

        @register_verb(list, context=Context.EVAL)
        def split(data, num):
            """Split a list into two lists by one of the numbers in the list"""
            return [[dat for dat in data if dat < num],
                    [dat for dat in data if dat > num]]

        @register_verb(list, context=Context.EVAL)
        def add(data, num):
            if not isinstance(num, int):
                num = list(num)
            else:
                num = [num] * len(data)
            return [dat + num[i] for i, dat in enumerate(data)]

        @add.register(int, context=Context.EVAL)
        def _(data, num):
            return data + num

        x = [1,2,3,4,5] >> split(4)
        self.assertEqual(x, [[1,2,3], [5]])
        x = [1,2,3,4,5] >> split(X[2])
        self.assertEqual(x, [[1,2], [4,5]])

        x = [1,2,3] >> add(2)
        self.assertEqual(x, [3,4,5])
        x = [1,2,3] >> add(X)
        self.assertEqual(x, [2,4,6])
        x = 1 >> add(1)
        self.assertEqual(x, 2)

    def test_int(self):
        X = Symbolic()

        @register_verb(int, context=Context.EVAL)
        def add(data, num):
            """Split a list into two lists by one of the numbers in the list"""
            return data + num

        self.assertEqual(1 >> add(1), 2)
        self.assertEqual(2 >> add(X), 4)
        self.assertEqual(2 >> add(X ** 3), 10)

    def test_register_func(self):
        X = Symbolic()
        self.assertEqual(repr(X), '<Symbolic:X>')

        @register_verb(dict, context=Context.EVAL)
        def filter(data, keys):
            return {key: val for key, val in data.items() if key in keys}

        @register_verb(dict, context=Context.EVAL)
        def length(data):
            return data.__len__()

        @register_func(context=Context.EVAL)
        def starts_with(data, prefix):
            return [key for key in data if key.startswith(prefix)]

        @register_func(context=Context.EVAL)
        def ends_with(data, suffix):
            return [key for key in data if key.endswith(suffix)]

        x = {'abc': 1, 'def': 2, 'ahi': 3} >> filter(['abc', 'def'])
        self.assertEqual(x, {'abc': 1, 'def': 2})
        x = {'abc': 1, 'def': 2, 'ahi': 3} >> filter(starts_with('a'))
        self.assertEqual(x, {'abc': 1, 'ahi': 3})
        self.assertEqual(x >> length(), 2)
        x = {'abc': 1, 'def': 2, 'ahi': 3} >> length()
        self.assertEqual(x, 3)
        x = {'abc': 1, 'def': 2, 'hic': 3} >> filter(ends_with('c'))
        self.assertEqual(x, {'abc': 1, 'hic': 3})

    def test_unary(self):
        X = Symbolic()
        @register_verb(dict, context=Context.SELECT)
        def filter(data, keys):
            if not isinstance(keys, list):
                keys = [keys]

            has_negs = all(key.startswith('-') for key in keys)
            if has_negs:
                keys = [key[1:] for key in keys]

            return {
                key: val
                for key, val in data.items()
                if (not has_negs and key in keys) or (has_negs and key not in keys)
            }

        @register_operator
        class MyOperators(Operator):

            def neg(self, x):
                return '-' + x

        x = {'abc': 1, 'ded': 2, 'hic': 3} >> filter(-X['abc'])
        self.assertEqual(x, {'ded': 2, 'hic': 3})

        x = {'abc': 1, 'ded': 2, 'hic': 'a'} >> filter(X['hic'])
        self.assertEqual(x, {'hic': 'a'})



        with self.assertRaises(TypeError):
            {} >> filter(1-X['abc'])

        register_operator(Operator)

    def test_compile_attrs(self):
        import types
        data = lambda: 0
        data.a = 1
        data.b = 2
        data.c = 3

        X = Symbolic()
        @register_verb(types.FunctionType, context=Context.EVAL)
        def filter_by_value(data, *values):
            return {
                key: getattr(data, key) for key in data.__dict__
                if getattr(data, key) in values
            }

        d = data >> filter_by_value(X.a, X.b)
        self.assertEqual(d, {'a': 1, 'b': 2})

    def test_binop(self):
        import types
        data = lambda: 0
        data.a = 1
        data.b = 2
        data.c = 3

        X = Symbolic()
        @register_verb(types.FunctionType, context=Context.EVAL)
        def add(data, *values):
            return sum(values)

        @register_operator
        class MyOperators(Operator):
            def add(self, me, other):
                return me + other

            def or_(self, me, other):
                return me - other

        self.assertEqual(data >> add(X.a + X.b, X.c), 6)
        self.assertEqual(data >> add(X.a & X.b, X.c), 3) # 1 & 2 = 0
        self.assertEqual(data >> add(X.a | X.b, X.c), 2) # 1 - 2 + 3
        register_operator(Operator)

    def test_unsupported_type_for_func(self):
        X = Symbolic()
        @register_verb(int, context=Context.EVAL)
        def add(data, other):
            return data + other

        @add.register(float, context=Context.EVAL)
        def _(data, other):
            return data * other

        @register_func(int, context=Context.EVAL)
        def one(data):
            return 1

        @register_func(context=Context.EVAL)
        def two(data):
            return 2

        x = 1 >> add(2)
        self.assertEqual(x, 3)

        x = 1 >> add(one())
        self.assertEqual(x, 2)

        x = 1.1 >> add(two())
        self.assertEqual(x, 2.2)

        with self.assertRaises(NotImplementedError):
            1.1 >> add(one())

        with self.assertRaises(NotImplementedError):
            'a' >> add(1)

    def test_operators(self):
        X = Symbolic()

        @register_verb(int, context=Context.EVAL)
        def add(data, arg):
            return data + arg

        x = 1 >> add(X + 1)
        self.assertEqual(x, 3)
        x = 1 >> add(X - 1)
        self.assertEqual(x, 1)
        x = 1 >> add(X * 1)
        self.assertEqual(x, 2)
        x = 1 >> add(X / 1)
        self.assertEqual(x, 2)
        x = 1 >> add(X // 1)
        self.assertEqual(x, 2)
        x = 1 >> add(X % 1)
        self.assertEqual(x, 1)
        x = 1 >> add(X << 1)
        self.assertEqual(x, 3)
        x = 1 >> add(X >> 1)
        self.assertEqual(x, 1)
        x = 1 >> add(X & 1)
        self.assertEqual(x, 2)
        x = 1 >> add(X | 1)
        self.assertEqual(x, 2)
        x = 1 >> add(X ^ 1)
        self.assertEqual(x, 1)
        x = 1 >> add(X ** 1)
        self.assertEqual(x, 2)
        x = 1 >> add(X < 1)
        self.assertEqual(x, 1)
        x = 1 >> add(X <= 1)
        self.assertEqual(x, 2)
        x = 1 >> add(X > 1)
        self.assertEqual(x, 1)
        x = 1 >> add(X >= 1)
        self.assertEqual(x, 2)
        x = 1 >> add(X == 1)
        self.assertEqual(x, 2)
        x = 1 >> add(X != 1)
        self.assertEqual(x, 1)
        x = 1 >> add(-X)
        self.assertEqual(x, 0)
        x = 1 >> add(+X)
        self.assertEqual(x, 2)
        x = 1 >> add(~X)
        self.assertEqual(x, -1)

        with self.assertRaises(TypeError):
            x = 1 >> add(X @ 1)
            # print(x)

    def test_error_changing_piping_sign(self):
        with self.assertRaises(ValueError):
            register_piping_sign('~')

    def test_proxy_compiler_set_data(self):
        X = Symbolic()

        @register_verb(FunctionType, context=Context.PENDING)
        def add1(data, arg):
            arg = evaluate_expr(arg, data, context=Context.EVAL)
            return data.a + arg

        @register_verb(FunctionType, context=Context.PENDING)
        def add2(data, arg):
            arg = evaluate_expr(arg, d2, Context.EVAL)
            return data.a + arg

        d1 = lambda: 0
        d2 = lambda: 0
        d1.a = 1
        d2.a = 10

        x = d1 >> add1(X.a)
        self.assertEqual(x, 2)

        x = d1 >> add2(X.a)
        self.assertEqual(x, 11)

    def test_proxy_compiler_custom(self):
        X = Symbolic()

        @register_verb(FunctionType, context=Context.PENDING)
        def add(data, arg):
            arg = evaluate_expr(arg, data, Context.EVAL) * 10
            return data.a + arg

        d1 = lambda: 0
        d1.a = 1

        x = d1 >> add(X.a)
        self.assertEqual(x, 11)

    def test_call_other_verbs_funcs(self):
        X = Symbolic()
        @register_verb(int, context=Context.EVAL)
        def add(data, other):
            return data + other

        @register_verb(int, context=Context.EVAL)
        def mul(data, other):
            return data * add(data, other)

        @register_func(context=Context.EVAL)
        def neg(data, num):
            return -num

        @register_func(context=Context.EVAL)
        def double_neg(data, num):
            return neg(data, num) * 2

        x = 2 >> add(1) >> mul(2) # 3 * (3 + 2)
        self.assertEqual(x, 15)

        x = 2 >> add(neg(1))
        self.assertEqual(x, 1)

        x = 2 >> add(double_neg(1))
        self.assertEqual(x, 0)

    def test_register_multiple(self):
        X = Symbolic()
        @register_verb(context=Context.EVAL)
        def add(data, other):
            return 0

        @add.register(int, context=Context.EVAL)
        @add.register(float, context=Context.EVAL)
        def _(data, other):
            return data + other

        x = 1 >> add(1)
        self.assertEqual(x, 2)

        x = 1.1 >> add(1.0)
        self.assertEqual(x, 2.1)

        x = 'a' >> add(1)
        self.assertEqual(x, 0)

    def test_complex(self):
        class Data:
            def __init__(self, **kwds):
                self.__dict__['data'] = kwds

            def __getattr__(self, name):
                if name == 'data':
                    return self.__dict__['data']
                return self.data[name]

            def __setattr__(self, name: str, value: Any) -> None:
                self.data[name] = value

            __getitem__ = __getattr__
            __setitem__ = __setattr__

        @register_verb(context=Context.SELECT)
        def select(data, *columns):
            return Data(**{key: data[key] for key in columns})

        @register_verb(context=Context.EVAL)
        def mutate(data, **kwds):
            data = data.data.copy()
            data.update(kwds)
            return Data(**data)

        @register_func(context=Context.EVAL)
        def mean(data, *columns):
            return [float(sum(columns)) / float(len(columns))]

        @register_func(context=Context.EVAL)
        def double(data, column):
            return [column * 2]

        f = Symbolic()
        d = Data(a=1, b=2, c=3)
        r = (d >> select(f.a, f.b) >>
                  mutate(c=double(f.a + f.b)[0], d=mean(f.a, f.b)[0]) >>
                  select(f.c, f.d))

        self.assertEqual(r.data, {'c': 6, 'd': 1.5})

        d = Data(a=Data(a=Data(a=Data(a=Data(a=1)))))
        r = (d >> mutate(a=double(f['a']['a']['a']['a']['a'])[0]))
        self.assertEqual(r.data, {'a': 2})
        r = (d >> mutate(a=double(f.a.a.a.a.a)[0]))
        self.assertEqual(r.data, {'a': 2})
        r = (d >> mutate(a=double(f.a['a'].a['a'].a)[0]))
        self.assertEqual(r.data, {'a': 2})
        r = (d >> mutate(a=double(f['a'].a['a'].a['a'])[0]))
        self.assertEqual(r.data, {'a': 2})
        r = (d >> mutate(a=1, b=2, c=3) >> mutate(a=2*f.c) >> select(f.a, f.b))
        self.assertEqual(r.data, {'a': 6, 'b': 2})

    def test_original_unaffected(self):
        @register_func((int, str))
        def func(data):
            return data
        @register_verb(context=Context.EVAL)
        def verb(data, x):
            return x

        self.assertEqual(1 >> verb(func()), 1)
        self.assertEqual(func(2), 2)
        self.assertEqual(func('2'), '2')

if __name__ == "__main__":
    unittest.main()
