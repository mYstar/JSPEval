""" Tests for the JspSolution class.
"""
import pytest
import numpy as np
from jspsolution import JspSolution
from test.conftest import isclose


@pytest.mark.parametrize("index,expected", [
    (0, 0),
    (1, 2),
    (2, 1),
    (3, 2),
    pytest.mark.xfail(raises=IndexError)((4, None)),
])
def test_determine_machine(model, index, expected):
    solution = JspSolution(model, [0.1, 0.4, 0.9, 0.2])
    np_solution = JspSolution(model, np.array([0.1, 0.4, 0.9, 0.2]))
    assert solution.get_machine_assignment(int(index)) == expected
    assert np_solution.get_machine_assignment(int(index)) == expected


@pytest.mark.parametrize("value,expected", [
    (0.03, 0),
    (0.12, 1),
    (0.28, 2),
    (0.33, 3),
    (0.47, 4),
    (0.59, 5),
    (0.61, 6),
    (0.77, 7),
    (0.82, 8),
    (0.98, 9),
])
def test_determine_10machine(model_10machines, value, expected):
    solution = JspSolution(model_10machines, [value])
    np_solution = JspSolution(model_10machines, np.array([value]))
    assert solution.get_machine_assignment(0) == expected
    assert np_solution.get_machine_assignment(0) == expected
    with pytest.raises(IndexError):
        solution.get_machine_assignment(1)
    with pytest.raises(IndexError):
        np_solution.get_machine_assignment(1)


@pytest.mark.parametrize("index,expected", [
    (0, 0.03*2),
    (1, 0.33*2),
    (2, 0.61),
    (3, 0.98*2-1),
])
def test_prioritiy(model, index, expected):
    solution = JspSolution(model, [0.03, 0.33, 0.61, 0.98])
    np_solution = JspSolution(model, np.array([0.03, 0.33, 0.61, 0.98]))
    assert isclose(solution.get_priority(index), expected)
    assert isclose(np_solution.get_priority(index), expected)


@pytest.mark.parametrize("value,expected", [
    (0.03, 0.3),
    (0.12, 0.2),
    (0.28, 0.8),
    (0.33, 0.3),
    (0.47, 0.7),
    (0.59, 0.9),
    (0.61, 0.1),
    (0.77, 0.7),
    (0.82, 0.2),
    (0.98, 0.8),
])
def test_priority_10machine(
        model_10machines,
        value,
        expected
):
    solution = JspSolution(model_10machines, [value])
    np_solution = JspSolution(model_10machines, np.array([value]))
    assert isclose(solution.get_priority(0), expected)
    assert isclose(np_solution.get_priority(0), expected)


@pytest.mark.xfail(raises=ValueError)
def test_do_not_allow_negative_allel(model):
    JspSolution(model, [-0.03, 0.33, 0.61, 0.98])


@pytest.mark.xfail(raises=ValueError)
def test_do_not_allow_allel_over_1(model):
    JspSolution(model, [1.03, 0.33, 0.61, 0.98])


@pytest.mark.xfail(raises=ValueError)
def test_do_not_allow_negative_allel_np(model):
    JspSolution(model, np.array([-0.03, 0.33, 0.61, 0.98]))


@pytest.mark.xfail(raises=ValueError)
def test_do_not_allow_allel_over_1_np(model):
    JspSolution(model, np.array([1.03, 0.33, 0.61, 0.98]))
