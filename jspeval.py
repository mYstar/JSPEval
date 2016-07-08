import copy
import numpy


class JspEvaluator:
    """
    This class provides a way to evaluate JspModels. A JspSolution can be given
    to several functions to calculate the following metrics:
        - makespan
        - total tardiness
        - load balancing
        - work in process
        - flowtime
    """

    def __init__(self, model):
        """
        Takes the model, that shall be used to calculate the metrics.
        """
        self.model = model

    def build_machine_assignment(self, solution):
        """
        This function assigns operations to machines according to a solution.
        The solution can be provided by an optimization-algorithm.

        solution: a solution for this model, that determines the machines and
        the priorities

        returns: a list containing for every machine the list of operations (as
        job, operation tuple) in the order of processing
        """
        if(self.model.solution_length() != len(solution)):
            raise ValueError("the solution does not fit the model (",
                             self.model.solution_length(),
                             " operations versus ",
                             len(solution), " solution length)")

        # create a dictionary of the operations and their priority per machine
        assignment = [{} for i in range(len(self.model.machine))]
        for index in range(len(solution)):
            machine_idx = solution.get_machine_assignment(index)
            global_idx = self.model.translate_global_index(index)
            priority = solution.get_priority(index)
            assignment[machine_idx][global_idx] = priority

        # priority sharing
        for machine_dict in assignment:
            for sol1 in machine_dict:
                for sol2 in machine_dict:
                    if(sol1 == sol2):
                        continue

                    job1 = sol1[0]
                    job2 = sol2[0]

                    if(job1 == job2):
                        op1 = sol1[1]
                        op2 = sol2[1]
                        prio1 = machine_dict[sol1]
                        prio2 = machine_dict[sol2]

                        # if the precedence of the operations is not correct
                        if(op1 < op2 and prio1 < prio2):
                            machine_dict[sol1] = prio2

        # sort all machine's assignments
        assignment = [sorted(machine_ass,
                             key=lambda sol: (-machine_ass[sol], sol[1]))
                      for machine_ass in assignment]
        return assignment

    def execute_schedule(self, solution):
        """
        This function takes a solution, which must fit the model (i.e. it must
        have priorities for the correct number of operations) and calculates
        schedule for it. This means the time when a particular job is done is
        calculated from the solution.

        solution: an array using the permutation based coding for every
        operation in the model

        returns:
            1. a list with the machine assignments (which is a list of
            operations for every machine)
            2. a dictionary with every operation and its corresponding
            finishtime and the used setuptime as a tuple like: (setup, finish)
        """
        assignment = self.build_machine_assignment(solution)
        ret_assignment = copy.deepcopy(assignment)

        schedule = {}
        # stores the finishing time of the last operation for every machine
        machinetime = [0.0 for i in range(len(assignment))]
        # stores the last processed operation for every machine
        last_op = [None for i in range(len(assignment))]

        for i in range(self.model.solution_length()):
            for machine in range(len(assignment)):
                # skip machines with empty queues
                if(len(assignment[machine]) == 0):
                    continue

                op_index = assignment[machine][0]
                # execute job only if the predecessor in the job is already
                # calculated or its the first operation in the job
                if(op_index[1] == 0 or
                   (op_index[0], op_index[1]-1) in schedule):

                    assignment[machine].pop(0)
                    job = self.model.job[op_index[0]]
                    operation = job.operation[op_index[1]]

                    # the first operation's starttime is the job's starttime
                    if(op_index[1] == 0):
                        starttime = job.starttime
                    else:
                        # all other operations can start when their predecessors
                        # are done
                        starttime = \
                            schedule[(op_index[0], op_index[1]-1)][1]

                    # calculate the setuptime
                    setuptime = self.model.get_setuptime(
                        last_op[machine],
                        op_index)

                    # calculate the time the operation is finished
                    finish_time =\
                        max(machinetime[machine], starttime) +\
                        operation.op_duration + setuptime

                    schedule[op_index] = (setuptime, finish_time)
                    machinetime[machine] = finish_time
                    last_op[machine] = op_index
                    break

        return ret_assignment, schedule

    def get_metrics(self, assignment, schedule):
        """
        Calculates the following metrics:
            * makespan
            * total tardiness

        assignment:     the machine assignment for the operations
        schedule:       The calculated schedule for a solution.

        returns:        a dictionary with the metric names as keys.
        """
        # search for the last readytime
        makespan = max(schedule.values(), key=lambda x: x[1])[1]

        # find the maximum readytime for each job and compare to the deadline
        job_ready = {}
        for op in schedule:
            if(job_ready.get(op[0], 0.0) < schedule[op][1]):
                job_ready[op[0]] = schedule[op][1]

        total_tardiness = 0.0
        for jobnum in job_ready:
            t_ready = job_ready[jobnum]
            deadline = self.model.job[jobnum].deadline
            if(t_ready > deadline):
                total_tardiness += t_ready - deadline

        # sum all production times for every machine
        m_prod_times = []
        for mach_id in range(len(assignment)):
            sum_prod = 0.0
            for op in assignment[mach_id]:
                sum_prod += self.model.job[op[0]].operation[op[1]].op_duration
            m_prod_times.append(sum_prod/makespan)
        # calculate the standard deviation
        loadbalance = numpy.std(m_prod_times)

        # sum all setuptimes
        setuptime = sum(times[0] for times in schedule.values())

        # calculate the WIP and passtime
        # create a list of all job start- and endtimes and their effects on the
        # WIP
        # use the start- and endtimes to calculate the passtime for the job
        wip_changes = {}
        max_passtime = 0
        for job_id in range(len(self.model.job)):
            last_op = len(self.model.job[job_id].operation) - 1
            jobstart = schedule[(job_id, 0)][1] -\
                self.model.job[job_id].operation[0].op_duration
            jobend = schedule[(job_id, last_op)][1]
            production_units = self.model.job[job_id].production_units
            wip_changes[jobstart] = production_units
            wip_changes[jobend] = -production_units

            # calculate the max passtime
            duration = jobend - jobstart
            if(max_passtime < duration):
                max_passtime = duration

        max_wip = 0
        curr_wip = 0
        for _, change in sorted(wip_changes.iteritems()):
            curr_wip += change
            if curr_wip > max_wip:
                max_wip = curr_wip

        return {"makespan": makespan,
                "setup time": setuptime,
                "load balance": loadbalance,
                "max wip": max_wip,
                "max passtime": max_passtime,
                "total tardiness": total_tardiness}
