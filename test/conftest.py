import pytest
from jspeval import JspEvaluator
from jspmodel import JspModel
from jspsolution import JspSolution

# === utilities === #


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


# === fixtures === #


@pytest.fixture(scope="module",
                params=["xml/example.xml"])
def model(request):
    # read the model and build objects from it
    return JspModel(request.param)


@pytest.fixture(scope="module")
def evaluator(model):
    return JspEvaluator(model)


@pytest.fixture(scope="module",
                params=["test/10machines.xml"])
def model_10machines(request):
    # read the model and build objects from it
    return JspModel(request.param)


@pytest.fixture(scope="module",
                params=["test/10operations.xml"])
def model_10operations(request):
    # read the model and build objects from it
    return JspModel(request.param)


@pytest.fixture(scope="module",
                params=["test/complexmodel.xml"])
def model_complex(request):
    # read the model and build objects from it
    return JspModel(request.param)


@pytest.fixture
def rand_solution(model):
    return model.get_random_solution()


@pytest.fixture
def simple_solution(model):
    length = model.solution_length()
    return JspSolution(model, [float(i)/length for i in range(length)])


@pytest.fixture
def simple_solution_10operations(model_10operations):
    length = model_10operations.solution_length()
    return JspSolution(
        model_10operations,
        [float(i)/length for i in range(length)])
