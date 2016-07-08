from lxml import etree
from lxml import objectify
from jspsolution import JspSolution
import numpy


class JspModel:

    def __init__(self, schemafile="xml/example.xml"):
        """
        Takes the xml-File, that describes the model and builds all necessary
        datastructures.
        """
        # read the xml schema and build a parser from it
        schema = etree.XMLSchema(file=open("xml/model.xsd", "r"))
        parser = objectify.makeparser(schema=schema)

        # read the model and build objects from it
        self.model = objectify.parse(open(schemafile, "r"), parser).getroot()
        # prebuild the index translation list
        self.index_translation_list = self._create_index_translation_list()
        # provide a translated list of the allowed machines for every operation
        self.allowed_machines = self._create_allowed_machines_list()
        # create a setupmatrix between all operations (indexed globally)
        self.setuptimes = self._create_setuptimes()

    def __getattr__(self, name):
        """
        Forwards the getter to a ObjectifiedObject of the model.
        """
        return getattr(self.model, name)

    def _create_allowed_machines_list(self):
        """
        Creates a dictionary which contains the ids of all allowed machines for
        every operation.
        """
        machine_ids = [machine.get("machine_id")
                       for machine in self.model.machine]
        allowed_machines = {}
        for i in range(len(self.model.job)):
            for j in range(len(self.model.job[i].operation)):
                allowed = [machine_ids.index(m_name.text) for m_name in
                           self.model.job[i].operation[j].allowed_machine]
                allowed_machines[(i, j)] = allowed

        return allowed_machines

    def _create_index_translation_list(self):
        """
        This function creates an array that is used to translate the global
        index (as used in the solution representation), where the Operations
        are all in one long sequence, to the job- and operation indexes of the
        model. This list shall only be calculated once for one model, because it
        will not change.

        returns:    a list consisting of tuples (job_index, operation_index)

        example:    [(0, 0), # 0: first operation will always have these indexes
                    (0, 1), # 1: first job, second operation
                    (1, 0), # 2: second job, first operation
                    ...]
        """
        translation_list = []

        for i in range(len(self.model.job)):
            for j in range(len(self.model.job[i].operation)):
                translation_list.append((i, j))

        return translation_list

    def _create_setuptimes(self):
        """
        This function creates a dictionary, which contains all operations
        (globally indexed) and stores the setuptime to each.
        """

        try:
            # create a translationdictionary for the operation's names
            operationnames = {}
            for i in range(len(self.model.job)):
                for j in range(len(self.model.job[i].operation)):
                    operationnames[self.model.job[i].operation[j]
                                   .get("operation_id")] = (i, j)

            # create a setuptimes dictionary, which uses the names as key
            namedsetuptimes =\
                {(s.from_operation, s.to_operation): s.setup_duration
                 for s in self.model.setuptimes.setuptime}

            # assemble the globally indexed list
            return {(operationnames[name[0]], operationnames[name[1]]):
                    namedsetuptimes[name]
                    for name in namedsetuptimes.keys()}
        except AttributeError:
            return {}

    def solution_length(self):
        """
        This function returns the number of operations in the model. This is
        also the allowed solution length.

        returns:    the calculated length (int)
        """
        return sum(
            [len([op.tag for op in job.operation]) for job in self.model.job]
        )

    def get_random_solution(self):
        """
        This function creates a random solution for the model. It uses the
        number of jobs from the model to determine the length of the solution.

        returns: an array representation of the solution. (representing a
        schedule)
        """
        ind_length = self.solution_length()
        return JspSolution(self, numpy.random.rand(ind_length))

    def translate_global_index(self, index):
        """
        This function translates a global operation index (as used in the
        solution representation) into a tuple, consisting of the job- and
        operation-index.

        index: the global index to translate (int)

        returns: a tuple (job_index, operation_index) (int, int)
        """

        return self.index_translation_list[index]

    def get_setuptime(self, op_from, op_to):
        """
        Returns the setuptime between two operations or 0.0 if there isnt any.
        """
        op_tuple = (op_from, op_to)
        if op_tuple in self.setuptimes:
            return self.setuptimes[op_tuple]
        else:
            return 0.0