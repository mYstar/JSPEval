""" Represents a solution that is coded permutation based. Provides means to
access the priority and machine assignment for every operation.
"""
import math


class JspSolution:
    """
    This class represents a solution for a JSP Model and provides functions to
    extract the machine assignment and the priority.
    """

    def __init__(self, model, sol_array):
        """
        Initializes the datastructures. Precalculates the machine assignment
        and priorities

        @param model: the model this solution shall be used in (from:
        JspEvaluator.model)
        @type model: L{jspmodel.JspModel}
        @param sol_array: array representation of the solution
        permutationbased Encoding)
        @type sol_array: list
        """
        self.model = model
        self.set_values(sol_array)

    def set_values(self, val_array):
        """Sets new valus for the solution. Resets all precalculations.

        :val_array: new values to set

        """
        self._values = val_array

        self.machine_assignment = None
        self.priorities = None

    def get_values(self):
        """Returns the value array.

        :returns: a List of values

        """
        return self._values

    def get_machine_assignment(self, index):
        """
        Returns the machine index, that the operation at the index in the
        solution is assigned to. Performs Precalculations if necessary.

        @param index: the local index of the operation in the solution
        @type index: number

        @return: the index of the assigned machine
        @rtype: number
        """
        if self.machine_assignment is None:
            self.machine_assignment =\
                [self._determine_machine_index(index)
                 for index, _ in enumerate(self._values)]

        return self.machine_assignment[index]

    def get_priority(self, index):
        """
        Returns the priority, that the operation at the index in the solution
        has. Performs Precalculations if necessary.

        @param index: the local index of the operation in the solution
        @type index: number

        @return: the priority for the operation on its machine
        @rtype: number
        """
        if self.priorities is None:
            self.priorities =\
                [self._determine_priority(index)
                 for index, _ in enumerate(self._values)]

        return self.priorities[index]

    def _determine_machine_index(self, index):
        """
        Function that determines on which machine an operation is processed.
        Only the for this operation allowed machines are considered.

        @param index: the index of the operation in the solution
        @type index: number

        @return: the machines index (int)
        @rtype: number
        """

        index = int(index)
        if self.get_values()[index] < 0.0 or self.get_values()[index] > 1.0:
            raise ValueError("the allel shall be between 0.0 and 1.0")

        operation, _, rel_index = self._get_operation_and_rel_index(index)

        return self.model.allowed_machines[operation][rel_index]

    def _determine_priority(self, index):
        """
        Function that determines the remainder, which is cleaned from the
        machine mapping, from the allel. This remainder is used for priority
        calculation.

        @param index: the index of the operation in the solution
        @type index: number

        @return: the priority
        @rtype: number
        """

        index = int(index)
        if self.get_values()[index] < 0.0 or self.get_values()[index] > 1.0:
            raise ValueError("the allel shall be between 0.0 and 1.0")

        _, num_machines, rel_index = self._get_operation_and_rel_index(index)

        return self.get_values()[index] * num_machines - rel_index

    def __getitem__(self, index):
        return self.get_values()[index]

    def __len__(self):
        """
        Returns the length of the value array.

        @return: the length of the solution
        @rtype: number
        """
        return len(self.get_values())

    def _get_operation_and_rel_index(self, index):
        """ Gets the job-operation tuple from a global index, and the relative
        index of the assigned machine.

        @param index: the local index of an operation

        @return: 3 values:
            the global index of the specified operation as tuple,
            the number of allowed machines for the operation and
            the local index of the assigned machine
        @rtype: (number, number), number, number
        """
        operation = self.model.translate_global_index(index)
        num_machines = len(self.model.allowed_machines[operation])
        # this is the index of the machine relative to the allowed machines
        rel_index = int(math.floor(num_machines * self.get_values()[index]))

        return operation, num_machines, rel_index
