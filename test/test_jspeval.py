import conftest
import pytest
from jspsolution import JspSolution
from jspeval import JspEvaluator


@pytest.mark.usefixtures("evaluator", "rand_solution")
def test_machine_assignment_everything_assigned(evaluator, rand_solution):
    assignment = evaluator.build_machine_assignment(rand_solution)

    # have values for every operation
    assert len(assignment) == 4


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


@pytest.mark.parametrize("operation, expected", [
    ((0, 0), (0, 0.0)),
    ((0, 1), (2, 0.5)),
    ((1, 0), (1, 0.5)),
    ((1, 1), (0, 0.5)),
])
@pytest.mark.usefixtures("evaluator", "simple_solution")
def test_machine_assignment_model_simple_solution(
    evaluator,
    simple_solution,
    operation,
    expected
):
    assignment = evaluator.build_machine_assignment(simple_solution)
    assert assignment[operation] == expected


@pytest.mark.parametrize("operation, expected", [
    ((0, 0), (0, 0.0)),
    ((0, 1), (0, 0.4)),
    ((0, 2), (0, 0.8)),
    ((1, 0), (1, 0.2)),
    ((1, 1), (1, 0.6)),
    ((1, 2), (2, 0.0)),
    ((1, 3), (2, 0.4)),
    ((2, 0), (2, 0.8)),
    ((2, 1), (3, 0.2)),
    ((2, 2), (3, 0.6)),
])
@pytest.mark.usefixtures("model_10operations",
                         "simple_solution_10operations")
def test_machine_assignment_model10operations_simple_solution(
    model_10operations,
    simple_solution_10operations,
    operation,
    expected
):
    evaluator = JspEvaluator(model_10operations)
    assignment = evaluator.build_machine_assignment(
        simple_solution_10operations)
    assert assignment[operation][0] == expected[0]
    assert conftest.isclose(assignment[operation][1], expected[1])


@pytest.mark.parametrize("operation, expected", [
    ((0, 0), (1, 0.58)),
    ((0, 1), (2, 0.46)),
    ((1, 0), (1, 0.55)),
    ((1, 1), (2, 0.66)),
])
@pytest.mark.usefixtures("evaluator")
def test_machine_assignment_model_special_solution(
    evaluator,
    operation,
    expected
):
    special_sol = JspSolution(evaluator.model,
                              [0.7868123262784397, 0.22609036724935294,
                               0.5564064121714216, 0.33262085267764774])
    assignment = evaluator.build_machine_assignment(special_sol)
    assert assignment[operation][0] == expected[0]
    assert conftest.isclose(
        assignment[operation][1], expected[1],
        abs_tol=0.0099)


@pytest.mark.parametrize("operation, expected", [
    ((0, 0), (2, 0.24)),
    ((0, 1), (3, 0.24)),
    ((0, 2), (2, 0.92)),
    ((1, 0), (3, 0.72)),
    ((1, 1), (3, 0.84)),
    ((1, 2), (0, 0.36)),
    ((1, 3), (2, 0.60)),
    ((2, 0), (1, 0.80)),
    ((2, 1), (3, 0.08)),
    ((2, 2), (3, 0.16)),
])
@pytest.mark.usefixtures("model_10operations")
def test_machine_assignment_model10operations_special_solution(
    model_10operations,
    operation,
    expected
):
    evaluator = JspEvaluator(model_10operations)
    special_sol = JspSolution(evaluator.model,
                              [0.56, 0.81, 0.73, 0.93, 0.96, 0.09,
                               0.65, 0.45, 0.77, 0.79])
    assignment = evaluator.build_machine_assignment(special_sol)
    assert assignment[operation][0] == expected[0]
    assert conftest.isclose(
        assignment[operation][1], expected[1],
        abs_tol=0.0099)


@pytest.mark.parametrize("operation, expected", [
    ((0, 0), (2, 0.86)),
    ((0, 1), (3, 0.42)),
    ((1, 0), (0, 0.99)),
    ((1, 1), (0, 0.34)),
    ((1, 2), (0, 0.21)),
    ((1, 3), (2, 0.47)),
    ((1, 4), (2, 0.92)),
    ((2, 0), (1, 0.92)),
    ((2, 1), (2, 0.33)),
    ((2, 2), (3, 0.16)),
    ((3, 0), (2, 0.08)),
    ((4, 0), (3, 0.47))
])
def test_machine_assignment_complexmodel_special_solution(
    model_complex,
    operation,
    expected
):
    evaluator = JspEvaluator(model_complex)
    special_sol = JspSolution(evaluator.model,
                              [0.93, 0.71, 0.33, 0.17, 0.07, 0.49, 0.64, 0.48,
                               0.33, 0.72, 0.52, 0.47])
    assignment = evaluator.build_machine_assignment(special_sol)
    assert assignment[operation][0] == expected[0]
    assert conftest.isclose(
        assignment[operation][1], expected[1],
        abs_tol=0.0099)


@pytest.mark.usefixtures("evaluator", "simple_solution")
def test_execute_schedule_right_output_len(evaluator, simple_solution):
    assignment, schedule = evaluator.execute_schedule(simple_solution)
    assert len(schedule) == 4
    assert len(assignment) == 4


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
    ((0, 0), (0.0, 70.0)),
    ((0, 1), (0.0, 85.0)),
    ((0, 2), (0.0, 90.0)),
    ((1, 0), (0.0, 25.0)),
    ((1, 1), (0.0, 50.0)),
    ((1, 2), (0.0, 60.0)),
    ((1, 3), (0.0, 65.0)),
    ((2, 0), (0.0, 35.0)),
    ((2, 1), (0.0, 90.0)),
    ((2, 2), (0.0, 100.0)),
])
@pytest.mark.usefixtures("model_10operations", "simple_solution_10operations")
def test_execute_schedule_special_solution_10_operations(
    model_10operations,
    operation,
    expected
):
    evaluator = JspEvaluator(model_10operations)
    solution = JspSolution(model_10operations,
                           [0.56, 0.81, 0.73, 0.93, 0.96, 0.09,
                            0.65, 0.45, 0.77, 0.79])
    _, schedule = evaluator.execute_schedule(solution)
    assert schedule[operation] == expected


@pytest.mark.parametrize("operation, expected", [
    ((0, 0), (0.0, 7.0)),
    ((0, 1), (5.5, 52.5)),
    ((1, 0), (0.0, 30.0)),
    ((1, 1), (0.0, 55.0)),
    ((1, 2), (1.5, 66.5)),
    ((1, 3), (0.0, 71.5)),
    ((1, 4), (0.0, 121.5)),
    ((2, 0), (0.0, 45.0)),
    ((2, 1), (0.0, 47.0)),
    ((2, 2), (0.0, 65.5)),
    ((3, 0), (0.0, 126.5)),
    ((4, 0), (0.0, 35.0)),
])
def test_execute_schedule_special_solution_complex(
    model_complex,
    operation,
    expected
):
    evaluator = JspEvaluator(model_complex)
    solution = JspSolution(model_complex,
                           [0.93, 0.71, 0.33, 0.17, 0.07, 0.49, 0.64, 0.48,
                            0.33, 0.72, 0.52, 0.47])
    _, schedule = evaluator.execute_schedule(solution)
    assert schedule[operation] == expected


def test_calculate_metrics_example_simple_solution(evaluator, simple_solution):
    assignment, schedule = evaluator.execute_schedule(simple_solution)
    metrics = evaluator.get_metrics(assignment, schedule)
    assert metrics["makespan"] == 60.0
    assert metrics["setup time"] == 0.0
    assert metrics["max wip"] == 1
    assert conftest.isclose(metrics["avg flowfactor"], 1.0)
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
    assert conftest.isclose(metrics["avg flowfactor"], 1.9375)
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
    assert conftest.isclose(metrics["avg flowfactor"], 1.0)
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
                           [0.56, 0.81, 0.73, 0.93, 0.96, 0.09,
                            0.65, 0.45, 0.77, 0.79])
    assignment, schedule = evaluator.execute_schedule(solution)
    metrics = evaluator.get_metrics(assignment, schedule)
    assert metrics["makespan"] == 100.0
    assert metrics["setup time"] == 0.0
    assert metrics["max wip"] == 5
    assert conftest.isclose(metrics["avg flowfactor"],
                            1.55555556,
                            abs_tol=0.000001)
    assert metrics["total tardiness"] == 115.0
    assert conftest.isclose(
            metrics["load balance"],
            0.24622144504490259)

def test_calculate_metrics_complex_solution(
    model_complex
):
    evaluator = JspEvaluator(model_complex)
    solution = JspSolution(model_complex,
                           [0.93, 0.71, 0.33, 0.17, 0.07, 0.49, 0.64, 0.48,
                            0.33, 0.72, 0.52, 0.47])
    assignment, schedule = evaluator.execute_schedule(solution)
    metrics = evaluator.get_metrics(assignment, schedule)
    assert metrics["makespan"] == 126.5
    assert metrics["setup time"] == 7.0
    assert metrics["max wip"] == 10
    assert conftest.isclose(metrics["avg flowfactor"], 1.3921553884711779)
    assert metrics["total tardiness"] == 84.0
    assert conftest.isclose(
            metrics["load balance"],
            0.15714880181131291)
