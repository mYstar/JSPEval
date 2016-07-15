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
        This function assigns operations to machines according to a solution   .
        and calculates their priorities. A solution can be provided by an     .
        optimization-algorithm                                               .

        solution: a solution for this model, that determines the machines and
        the priorities

        returns: a dictionary for every operation containing its determined
        machine and priority. Like: (job, op): (machine, prio)
        """
        if(self.model.solution_length() != len(solution)):
            raise ValueError("the solution does not fit the model (",
                             self.model.solution_length(),
                             " operations versus ",
                             len(solution), " solution length)")

        # create a dictionary of the operations and their priority per machine
        assignment = {}
        for index in range(len(solution)):
            machine_idx = solution.get_machine_assignment(index)
            global_idx = self.model.translate_global_index(index)
            priority = solution.get_priority(index)
            assignment[global_idx] = (machine_idx, priority)

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
            1. a list with the machine assignments (which is a dict of all
            operations with containing a tuple (machine, priority) for every
            one)
            2. a dictionary with every operation and its corresponding
            finishtime and the used setuptime as a tuple like: (setup, finish)
        """
        assignment = self.build_machine_assignment(solution)

        schedule = {}
        # stores the finishing time of the last operation for every machine
        machinetime = [0.0 for i in range(len(self.model.machine))]
        # stores the last processed operation for every machine
        last_op = [None for i in range(len(self.model.machine))]
        # init the dict of available operations + their machines and priorities
        avail_op = {}
        for i in range(len(self.model.job)):
            avail_op[(i, 0)] = assignment[(i, 0)]

        # calculate execution of all operations in order
        for i in range(self.model.solution_length()):
            # get the available operation with the highest priority
            op_index = max(avail_op.keys(), key=lambda x: avail_op[x][1])
            job = self.model.job[op_index[0]]
            operation = job.operation[op_index[1]]
            machine = avail_op[op_index][0]

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
            if machinetime[machine] + setuptime > starttime:
                start = machinetime[machine] + setuptime
            else:
                start = starttime
                # readjust hidden setuptime (done in idle time)
                setuptime = 0.0
            finish_time = start + operation.op_duration

            schedule[op_index] = (setuptime, finish_time)

            # cleanup
            machinetime[machine] = finish_time
            last_op[machine] = op_index
            del avail_op[(op_index[0], op_index[1])]
            # insert next operation into available list, if this was not the
            # last
            if(op_index[1] < len(self.model.job[op_index[0]].operation) - 1):
                avail_op[(op_index[0], op_index[1]+1)] =\
                    assignment[(op_index[0], op_index[1]+1)]

        return assignment, schedule

    def get_metrics(self, assignment, schedule):
        """
        Calculates the following metrics:
            * makespan
            * total tardiness
            * load balance
            * setup time
            * max wip
            * max passtime

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
        m_prod_times = [0.0 for idx in range(len(self.model.machine))]
        for op, assign in assignment.iteritems():
            m_prod_times[assign[0]] +=\
                self.model.job[op[0]].operation[op[1]].op_duration
        for idx in range(len(m_prod_times)):
            m_prod_times[idx] = m_prod_times[idx]/makespan
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
