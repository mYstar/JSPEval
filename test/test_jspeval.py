import conftest
import pytest
from jspsolution import JspSolution
from jspeval import JspEvaluator


@pytest.mark.usefixtures("evaluator", "rand_solution")
def test_machine_assignment_everything_assigned(evaluator, rand_solution):
    assignment = evaluator.build_machine_assignment(rand_solution)

    # have a list for every machine
    assert len(assignment) == 3

    # make sure the correct number of operations have been assigned
    ops = 0
    for mlist in assignment:
        ops += len(mlist)

    assert ops == 4


@pytest.mark.parametrize("array", [
    pytest.mark.xfail(raises=IndexError)([0, 0, 0]),
    pytest.mark.xfail(raises=IndexError)([0, 0, 0, 0, 0]),
])
@pytest.mark.usefixtures("evaluator")
def test_machine_assignment_dont_accept_unfitting_solutions(
    evaluator,
    array
):
    JspSolution(evaluator.model, array)


@pytest.mark.parametrize("machine_index, op_index, expected", [
    (0, 0, (1, 1)),
    (0, 1, (0, 0)),
    (1, 0, (1, 0)),
    (2, 0, (0, 1)),
    pytest.mark.xfail(raises=IndexError)((3, 0, None)),
    pytest.mark.xfail(raises=IndexError)((0, 2, None)),
    pytest.mark.xfail(raises=IndexError)((1, 1, None)),
    pytest.mark.xfail(raises=IndexError)((2, 1, None)),
])
@pytest.mark.usefixtures("evaluator", "simple_solution")
def test_machine_assignment_model_simple_solution(
    evaluator,
    simple_solution,
    machine_index,
    op_index,
    expected
):
    assignment = evaluator.build_machine_assignment(simple_solution)
    assert assignment[machine_index][op_index] == expected


@pytest.mark.parametrize("machine_index, op_index, expected", [
    (0, 0, (0, 0)),
    (0, 1, (0, 1)),
    (0, 2, (0, 2)),
    (1, 0, (1, 0)),
    (1, 1, (1, 1)),
    (2, 0, (2, 0)),
    (2, 1, (1, 2)),
    (2, 2, (1, 3)),
    (3, 0, (2, 1)),
    (3, 1, (2, 2)),
    pytest.mark.xfail(raises=IndexError)((4, 0, None)),
    pytest.mark.xfail(raises=IndexError)((0, 3, None)),
    pytest.mark.xfail(raises=IndexError)((1, 2, None)),
    pytest.mark.xfail(raises=IndexError)((2, 3, None)),
    pytest.mark.xfail(raises=IndexError)((3, 2, None)),
])
@pytest.mark.usefixtures("model_10operations",
                         "simple_solution_10operations")
def test_machine_assignment_model10operations_simple_solution(
    model_10operations,
    simple_solution_10operations,
    machine_index,
    op_index,
    expected
):
    evaluator = JspEvaluator(model_10operations)
    assignment = evaluator.build_machine_assignment(
        simple_solution_10operations)
    assert assignment[machine_index][op_index] == expected


@pytest.mark.parametrize("machine_index, op_index, expected", [
    (1, 0, (0, 0)),
    (1, 1, (1, 0)),
    (2, 0, (1, 1)),
    (2, 1, (0, 1)),
    pytest.mark.xfail(raises=IndexError)((3, 0, None)),
    pytest.mark.xfail(raises=IndexError)((0, 0, None)),
    pytest.mark.xfail(raises=IndexError)((1, 2, None)),
    pytest.mark.xfail(raises=IndexError)((2, 2, None)),
])
@pytest.mark.usefixtures("evaluator")
def test_machine_assignment_model_special_solution(
    evaluator,
    machine_index,
    op_index,
    expected
):
    special_sol = JspSolution(evaluator.model,
                              [0.7868123262784397, 0.22609036724935294,
                               0.5564064121714216, 0.33262085267764774])
    assignment = evaluator.build_machine_assignment(special_sol)
    assert assignment[machine_index][op_index] == expected


@pytest.mark.parametrize("machine_index, op_index, expected", [
    (0, 0, (2, 1)),
    (0, 1, (1, 1)),
    (1, 0, (1, 2)),
    (1, 1, (1, 3)),
    (1, 2, (0, 0)),
    (1, 3, (0, 1)),
    (2, 0, (0, 2)),
    (2, 1, (2, 0)),
    (2, 2, (2, 2)),
    (3, 0, (1, 0)),
    pytest.mark.xfail(raises=IndexError)((4, 0, None)),
    pytest.mark.xfail(raises=IndexError)((0, 2, None)),
    pytest.mark.xfail(raises=IndexError)((1, 4, None)),
    pytest.mark.xfail(raises=IndexError)((2, 3, None)),
    pytest.mark.xfail(raises=IndexError)((3, 1, None)),
])
@pytest.mark.usefixtures("model_10operations")
def test_machine_assignment_model10operations_special_solution(
    model_10operations,
    machine_index,
    op_index,
    expected
):
    evaluator = JspEvaluator(model_10operations)
    special_sol = JspSolution(evaluator.model,
                              [0.26289654, 0.37875545, 0.65186909, 0.87012503,
                               0.12016336, 0.43416026, 0.46744025, 0.5454204,
                               0.1569579, 0.61702519])
    assignment = evaluator.build_machine_assignment(special_sol)
    assert assignment[machine_index][op_index] == expected


@pytest.mark.usefixtures("evaluator", "simple_solution")
def test_execute_schedule_right_output_len(evaluator, simple_solution):
    assignment, schedule = evaluator.execute_schedule(simple_solution)
    assert len(schedule) == 4
    assert len(assignment) == 3


@pytest.mark.parametrize("operation, expected", [
    ((0, 0), (0.0, 45.0)),
    ((0, 1), (0.0, 60.0)),
    ((1, 0), (0.0, 25.0)),
    ((1, 1), (0.0, 40.0)),
])
@pytest.mark.usefixtures("evaluator", "simple_solution")
def test_execute_schedule_simple_solution(evaluator,
                                          simple_solution,
                                          operation,
                                          expected
                                          ):
    _, schedule = evaluator.execute_schedule(simple_solution)
    assert schedule[operation] == expected


@pytest.mark.parametrize("operation, expected", [
    ((0, 0), (0.0, 5.0)),
    ((0, 1), (2.5, 57.5)),
    ((1, 0), (0.0, 25.0)),
    ((1, 1), (0.0, 40.0)),
])
@pytest.mark.usefixtures("evaluator")
def test_execute_schedule_special_solution(evaluator, operation, expected):

    special_solution = JspSolution(evaluator.model,
                                   [0.7868123262784397, 0.22609036724935294,
                                    0.5564064121714216, 0.33262085267764774])
    _, schedule = evaluator.execute_schedule(special_solution)
    assert schedule[operation] == expected


@pytest.mark.parametrize("operation, expected", [
    ((0, 0), (0.0, 5.0)),
    ((0, 1), (0.0, 20.0)),
    ((0, 2), (0.0, 25.0)),
    ((1, 0), (0.0, 25.0)),
    ((1, 1), (0.0, 50.0)),
    ((1, 2), (0.0, 60.0)),
    ((1, 3), (0.0, 65.0)),
    ((2, 0), (0.0, 35.0)),
    ((2, 1), (0.0, 40.0)),
    ((2, 2), (0.0, 50.0)),
])
@pytest.mark.usefixtures("model_10operations", "simple_solution_10operations")
def test_execute_schedule_simple_solution_10_operations(
    model_10operations,
    simple_solution_10operations,
    operation,
    expected
):
    evaluator = JspEvaluator(model_10operations)
    _, schedule = evaluator.execute_schedule(simple_solution_10operations)
    assert schedule[operation] == expected


@pytest.mark.parametrize("operation, expected", [
    ((0, 0), (0.0, 5.0)),
    ((0, 1), (0.0, 65.0)),
    ((0, 2), (0.0, 70.0)),
    ((1, 0), (0.0, 25.0)),
    ((1, 1), (0.0, 50.0)),
    ((1, 2), (0.0, 60.0)),
    ((1, 3), (0.0, 75.0)),
    ((2, 0), (0.0, 35.0)),
    ((2, 1), (0.0, 70.0)),
    ((2, 2), (0.0, 80.0)),
])
@pytest.mark.usefixtures("model_10operations", "simple_solution_10operations")
def test_execute_schedule_special_solution_10_operations(
    model_10operations,
    operation,
    expected
):
    evaluator = JspEvaluator(model_10operations)
    solution = JspSolution(model_10operations,
                           [0.5572241803936271, 0.8146056708861297,
                            0.7334878579497098, 0.9348902571852687,
                            0.9630020818043674, 0.09038641982878015,
                            0.6450835364231192, 0.4521901964567513,
                            0.7731538645471703, 0.7904693381618841])
    _, schedule = evaluator.execute_schedule(solution)
    assert schedule[operation] == expected


def test_calculate_metrics_example_simple_solution(evaluator, simple_solution):
    assignment, schedule = evaluator.execute_schedule(simple_solution)
    metrics = evaluator.get_metrics(assignment, schedule)
    assert metrics["makespan"] == 60.0
    assert metrics["setup time"] == 0.0
    assert metrics["max wip"] == 1
    assert metrics["max passtime"] == 30.0
    assert metrics["total tardiness"] == 35.0
    assert conftest.isclose(
            metrics["load balance"],
            0.039283710065919297)


def test_calculate_metrics_example_special_solution(evaluator):
    special_sol = JspSolution(evaluator.model,
                              [0.7868123262784397, 0.22609036724935294,
                               0.5564064121714216, 0.33262085267764774])
    assignment, schedule = evaluator.execute_schedule(special_sol)
    metrics = evaluator.get_metrics(assignment, schedule)
    assert metrics["makespan"] == 57.5
    assert metrics["setup time"] == 2.5
    assert metrics["max wip"] == 2
    assert metrics["max passtime"] == 57.5
    assert metrics["total tardiness"] == 32.5
    assert conftest.isclose(
            metrics["load balance"],
            0.21690767459559079)


def test_calculate_metrics_10operations_simple_solution(
    model_10operations,
    simple_solution_10operations
):
    evaluator = JspEvaluator(model_10operations)
    assignment, schedule = evaluator.execute_schedule(
            simple_solution_10operations)
    metrics = evaluator.get_metrics(assignment, schedule)
    assert metrics["makespan"] == 65.0
    assert metrics["setup time"] == 0.0
    assert metrics["max wip"] == 6
    assert metrics["max passtime"] == 55.0
    assert metrics["total tardiness"] == 0.0
    assert conftest.isclose(
            metrics["load balance"],
            0.13867504905630729)


def test_calculate_metrics_10operations_special_solution(
    model_10operations,
    simple_solution_10operations
):
    evaluator = JspEvaluator(model_10operations)
    solution = JspSolution(model_10operations,
                           [0.5572241803936271, 0.8146056708861297,
                            0.7334878579497098, 0.9348902571852687,
                            0.9630020818043674, 0.09038641982878015,
                            0.6450835364231192, 0.4521901964567513,
                            0.7731538645471703, 0.7904693381618841])
    assignment, schedule = evaluator.execute_schedule(solution)
    metrics = evaluator.get_metrics(assignment, schedule)
    assert metrics["makespan"] == 80.0
    assert metrics["setup time"] == 0.0
    assert metrics["max wip"] == 6
    assert metrics["max passtime"] == 70.0
    assert metrics["total tardiness"] == 75.0
    assert conftest.isclose(
            metrics["load balance"],
            0.30777680630612825)
