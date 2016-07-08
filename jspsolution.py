import math


class JspSolution:
    """
    This class represents a solution for a JSP Model and provides functions to
    extract the machine assignment and the priority.
    """

    def __init__(self, model, sol_array):
        """
        Initializes the datastructures. Precalculates the machine assignment and
        priorities

        model:      the model this solution shall be used in (from:
                    JspEvaluator.model)
        sol_array:  array representation of the solution (permutationbased
                    Encoding)
        """
        self.model = model
        self.values = sol_array
        self.machine_assignment =\
            [self._determine_machine_index(index)
             for index in range(len(sol_array))]
        self.priorities =\
            [self._determine_priority(index)
             for index in range(len(sol_array))]

    def get_machine_assignment(self, index):
        """
        Returns the machine index, that the operation at the index in the
        solution is assigned to.
        """
        return self.machine_assignment[index]

    def get_priority(self, index):
        """
        Returns the priority, that the operation at the index in the solution
        has.
        """
        return self.priorities[index]

    def _determine_machine_index(self, index):
        """
        Function that determines on which machine an operation is processed.
        Only the for this operation allowed machines are considered.

        index:      the index of the operation in the solution

        returns:    the machines index (int)
        """

        index = int(index)
        if(self.values[index] < 0.0 or self.values[index] > 1.0):
            raise ValueError("the allel shall be between 0.0 and 1.0")

        operation = self.model.translate_global_index(index)
        num_machines = len(self.model.allowed_machines[operation])
        # this is the index of the machine relative to the allowed machines
        rel_index = int(math.floor(num_machines * self.values[index]))

        return self.model.allowed_machines[operation][rel_index]

    def _determine_priority(self, index):
        """
        Function that determines the remainder, which is cleaned from the
        machine mapping, from the allel. This remainder is used for priority
        calculation.

        index:      the index of the operation in the solution

        returns:    the priotity (float)
        """

        index = int(index)
        if(self.values[index] < 0.0 or self.values[index] > 1.0):
            raise ValueError("the allel shall be between 0.0 and 1.0")

        operation = self.model.translate_global_index(index)
        num_machines = len(self.model.allowed_machines[operation])
        rel_index = int(math.floor(num_machines * self.values[index]))

        return self.values[index] * num_machines - rel_index

    def __getitem__(self, index):
        return self.values[index]

    def __len__(self):
        """
        Returns the length of the value array.
        """
        return len(self.values)
