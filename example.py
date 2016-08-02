"""An example how to use the Jsp Evaluator
"""
from jspeval import JspEvaluator
from jspmodel import JspModel
from jspsolution import JspSolution


def example_func():
    """Demonstrates the usage of JspEval, JspModel and JspSolution.
    """
    # instanciate a model
    model = JspModel("xml/example.xml")

    # create solutions
    # random
    random_solution = model.get_random_solution()
    # custom
    custom_solution = JspSolution(model, [0.0, 0.25, 0.75, 0.5])

    # instanciate an evaluator for the solutions
    evaluator = JspEvaluator(model)

    # generate the machine assignments for the solutions
    random_assign = evaluator.build_machine_assignment(random_solution)
    custom_assign = evaluator.build_machine_assignment(custom_solution)

    # calculate the schedules for the solutions
    random_sched = evaluator.execute_schedule(random_assign)
    custom_sched = evaluator.execute_schedule(custom_assign)

    # calculate the metrics for the assignment and schedules
    random_metrics = evaluator.get_metrics(random_assign, random_sched)
    custom_metrics = evaluator.get_metrics(custom_assign, custom_sched)

    # print the metrics out
    print("random solution:")
    for metric in random_metrics:
        print(metric, ": ", random_metrics[metric], sep="")

    print()
    print("custom solution:")
    for metric in custom_metrics:
        print(metric, ": ", custom_metrics[metric], sep="")

if __name__ == "__main__":
    example_func()
