""" This module contains the JspModel class. It reads the models from xml file
and shares utility functions to the outside. Also shares the objectified view
on the xml model.
"""
import sys
import os.path
import gzip
import numpy
from lxml import etree
from lxml import objectify
sys.path.append(os.path.dirname(__file__))
from jspsolution import JspSolution


class JspModel:
    """ Reads all model information from a xml file. Provides solution
    length detection (solution_length()), creation of random solutions
    (get_random_solution()), index translation (translate_global_index()) and
    setuptimes for the operations (get_setuptime()).
    """

    def __init__(self, filename="xml/example.xml"):
        """
        Takes the xml-File, that describes the model and builds all necessary
        datastructures.
        """
        # read the xml schema and build a parser from it
        schemafile = "{}/xml/model.xsd".format(os.path.dirname(__file__))
        schema = etree.XMLSchema(file=open(schemafile, "r"))
        parser = objectify.makeparser(schema=schema)

        # read the model and build objects from it
        if filename.endswith(".gz"):
            modelfile = gzip.open(filename, 'r')
        else:
            modelfile = open(filename, 'r')

        self.model = objectify.parse(modelfile, parser).getroot()
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
        for i, _ in enumerate(self.model.job):
            for j, operation in enumerate(self.model.job[i].operation):
                allowed = [machine_ids.index(m_name.text) for m_name in
                           operation.allowed_machine]
                allowed_machines[(i, j)] = allowed

        return allowed_machines

    def _create_index_translation_list(self):
        """
        This function creates an array that is used to translate the global
        index (as used in the solution representation), where the Operations
        are all in one long sequence, to the job- and operation indexes of the
        model. This list shall only be calculated once for one model, because
        it will not change.

        @return: a list consisting of tuples (job_index, operation_index)
        example: [(0, 0), # 0: first operation will always have these indexes
        @rtype: list

                  (0, 1), # 1: first job, second operation
                  (1, 0), # 2: second job, first operation
                  ...]
        """
        translation_list = []

        for i, _ in enumerate(self.model.job):
            for j, _ in enumerate(self.model.job[i].operation):
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
            for i, _ in enumerate(self.model.job):
                for j, operation in enumerate(self.model.job[i].operation):
                    operationnames[operation.get("operation_id")] = (i, j)

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

        @return: the calculated length
        @rtype: number
        """
        return sum(
            [len([op.tag for op in job.operation]) for job in self.model.job]
        )

    def get_random_solution(self):
        """
        This function creates a random solution for the model. It uses the
        number of jobs from the model to determine the length of the solution.

        @return: an array representation of the solution. (convertible into a
        schedule)
        @rtype: list
        """
        ind_length = self.solution_length()
        return JspSolution(self, numpy.random.rand(ind_length))

    def translate_global_index(self, index):
        """
        This function translates a global operation index (as used in the
        solution representation) into a tuple, consisting of the job- and
        operation-index.

        @param index: the global index to translate (int)
        @type index: number

        @return: a tuple (job_index, operation_index)
        @rtype: number, number
        """

        return self.index_translation_list[index]

    def get_setuptime(self, op_from, op_to):
        """
        Returns the setuptime between two operations or 0.0 if there isnt any.

        @return: the setuptime
        @rtype: number
        """
        op_tuple = (op_from, op_to)
        if op_tuple in self.setuptimes:
            return self.setuptimes[op_tuple]
        else:
            return 0.0

    def __eq__(self, other):
        """Implements a comparison of 2 JspModels.

        :other: the JspModel to compare to.
        :returns: a boolean value, True if the models are equal from a xml
        standpoint

        """
        return _xmleq(self.model, other.model)

    def __ne__(self, other):
        """Implements a comparison of 2 JspModels.

        :other: the JspModel to compare to.
        :returns: a boolean value, False if the models are equal from a xml
        standpoint

        """
        return not _xmleq(self.model, other.model)


def _xmleq(elem1, elem2):
    """Compares 2 objectified lxml elements.

    :elem1: first element of the comparison
    :elem2: second element of the comparison
    :returns: boolean value, True if the elements are equal from an xml
    standpoint

    """
    if elem1.tag != elem2.tag or elem1.attrib != elem2.attrib:
        return False
    if elem1.text != elem2.text or elem1.tail != elem2.tail:
        return False
    if len(elem1) != len(elem2):
        return False

    for subel1, subel2 in zip(
            elem1.iterchildren(tag=etree.Element),
            elem2.iterchildren(tag=etree.Element)):
        if not _xmleq(subel1, subel2):
            return False

    return True
