""" Tests for the JspModel class.
"""
import pytest
from jspmodel import JspModel


def test_random_solution_length(rand_solution):
    assert len(rand_solution) == 4


def test_random_solution_range(rand_solution):
    for operation in rand_solution:
        assert operation >= 0.0
        assert operation <= 1.0


def test_solution_length(model, model_10operations):
    assert model.solution_length() == 4
    assert model_10operations.solution_length() == 10


@pytest.mark.parametrize("index, expected", [
    (0, (0, 0)),
    (1, (0, 1)),
    (2, (1, 0)),
    (3, (1, 1)),
    (-1, (1, 1)),
    pytest.mark.xfail(raises=IndexError)((4, None)),
])
def test_create_index_translation_list(model, index, expected):
    assert model.translate_global_index(index) == expected


@pytest.mark.parametrize("index, expected", [
    (0, (0, 0)),
    (1, (0, 1)),
    (2, (0, 2)),
    (3, (1, 0)),
    (4, (1, 1)),
    (5, (1, 2)),
    (6, (1, 3)),
    (7, (2, 0)),
    (8, (2, 1)),
    (9, (2, 2)),
    (-1, (2, 2)),
    pytest.mark.xfail(raises=IndexError)((10, None)),
])
def test_create_index_translation_list_10operations(
        model_10operations,
        index,
        expected
):
    assert model_10operations.translate_global_index(index) == expected


@pytest.mark.parametrize("index, expected", [
    (0, (0, 0)),
    (1, (0, 1)),
    (2, (1, 0)),
    (3, (1, 1)),
    (-1, (1, 1)),
    pytest.mark.xfail(raises=IndexError)((4, None)),
])
def test_translate_global_index(model, index, expected):
    assert model.translate_global_index(index) == expected


@pytest.mark.parametrize("from_, to_, expected", [
    ((0, 0), (0, 1), 2.0),
    ((0, 1), (0, 0), 1.5),
    ((0, 1), (1, 0), 5.5),
    ((0, 1), (1, 1), 0.0),
    ((0, 0), (1, 1), 0.0)
])
def test_setuptimes(model, from_, to_, expected):
    assert model.get_setuptime(from_, to_) == expected


def test_read_compressed_file(model):
    comp_model = JspModel("xml/example.xml.gz")
    assert comp_model == model


def test_equality_operator(model):
    assert model == JspModel("xml/example.xml")
    assert not model != JspModel("xml/example.xml")
    assert model != JspModel("test/10operations.xml")
    assert not model == JspModel("test/10operations.xml")
