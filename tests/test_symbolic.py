import pytest
from pipda.symbolic import SubsetRef
from pipda import *

def test_symbolic():
    f = Symbolic()
    assert isinstance(f.a, SubsetRef)
    assert isinstance(f['a'], SubsetRef)
    assert f.evaluate(1) == 1

def test_subsetref():
    f = Symbolic()
    assert f.a.evaluate(1, Context.NAME) == 'a'
    assert f['a'].evaluate(1, Context.NAME) == 'a'
    assert f['a'].evaluate({'a': 2}, Context.DATA) == 2
    assert isinstance(f.a.evaluate(1), SubsetRef)
    assert isinstance(f.a.a, SubsetRef)
    assert isinstance(f.a['a'], SubsetRef)
    expr = f['a']['a']
    assert expr.evaluate({'a': {'a': 2}}) == 2

    with pytest.raises(TypeError):
        f[1].evaluate(0, Context.NAME)