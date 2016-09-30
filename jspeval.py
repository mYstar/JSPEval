"""
Evaluator module.

Holds the class JspEvaluator, which is used for evaluation of JspSolution and
calculating machine assignments, schedules and metrics.
"""
import numpy


class JspEvaluator:
    """
    This class provides a way to evaluate JspModels. A JspSolution can be given
    to several functions to calculate the following metrics:
        - makespan
        - total tardiness
        - total setuptimes
        - load balancing
        - work in process (WIP)
        - flowtime
    """

    def __init__(self, model):
        """
        Takes the model, that shall be used to calculate the metrics.
        """
        self.model = model

    def metrics_count(self):
        """Returns the number of metric values that will be returned by the
           calculation.
        """
        return 6

    def build_machine_assignment(self, solution):
        """
        This function assigns operations to machines according to a solution
        and calculates their priorities. A solution can be provided by an
        optimization-algorithm.

        @param solution: a solution for this model, that determines the
        machines and the priorities

        @return: a dictionary for every operation containing its determined
        machine and priority. Like: (job, op): (machine, prio)
        @rtype: dict
        """
        if self.model.solution_length() != len(solution):
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

    def execute_schedule(self, assignment):
        """
        This function takes an assignment, which must fit the model (i.e.
        it must have priorities for the correct number of operations) and
        calculates schedule for it. This means the time when a particular job
        is done is calculated from the assignment.

        @param assignment: an dictionary holding the assigned machine and the
        calculated priority for every operation (in global notation). Like:
        (job, op): (machine, prio)
        @type assignment: dict

        @return: a dictionary with every operation and its corresponding
        finishtime and the used setuptime as a tuple like: (job, op): (setup,
        finish)
        @rtype: dict
        """

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

            # the first operation's releasetime is the job's releasetime
            if op_index[1] == 0:
                releasetime = job.releasetime
            else:
                # all other operations can start when their predecessors
                # are done
                releasetime = \
                    schedule[(op_index[0], op_index[1]-1)][1]

            # calculate the setuptime
            setuptime = self.model.get_setuptime(
                last_op[machine],
                op_index)

            # calculate the time the operation is finished
            if machinetime[machine] + setuptime > releasetime:
                start = machinetime[machine] + setuptime
                # calculate partial setuptimes if necessary
                if releasetime > machinetime[machine]:
                    setuptime -= releasetime - machinetime[machine]
            else:
                start = releasetime
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
            if op_index[1] < len(self.model.job[op_index[0]].operation) - 1:
                avail_op[(op_index[0], op_index[1]+1)] =\
                    assignment[(op_index[0], op_index[1]+1)]

        return schedule

    def get_metrics(self, assignment, schedule):
        """
        Calculates the following metrics:
            - makespan
            - total weighted tardiness
            - flowfactor
            - load balance
            - setup time
            - max wip

        @param assignment:     the machine assignment for the operations
        @type assignment: dict
        @param schedule:       The calculated schedule for a solution.
        @type schedule: dict

        @return:        a tuple with the metric values in the above order.
        @rtype: dict
        """
        # search for the last readytime
        makespan = max(schedule.values(), key=lambda x: x[1])[1]

        # calculate tardiness
        twt = self._calc_tardiness(schedule)

        # calculate the loadbalance
        loadbalance = self._calc_loadbalance(assignment, makespan)

        # sum all setuptimes
        setuptime = sum(times[0] for times in schedule.values())

        # calculate the WIP and flowfactor
        wip, flowfactor = self._calc_wip_and_flow(schedule)

        return [makespan, twt, flowfactor, setuptime, loadbalance, wip]

    def _calc_tardiness(self, schedule):
        """ Calculates the maximum timespan a job in schedule is too late.

        @param schedule: the schedule to calculate the tardiness for
        @type schedule: dict

        @return:  the tardiness value
        @rtype: number
        """
        # find the maximum readytime for each job and compare to the
        # deadline
        job_ready = {}
        for op_id in schedule:
            if job_ready.get(op_id[0], 0.0) < schedule[op_id][1]:
                job_ready[op_id[0]] = schedule[op_id][1]

        twt = 0.0
        for jobnum in job_ready:
            t_ready = job_ready[jobnum]
            deadline = self.model.job[jobnum].deadline
            weight = self.model.job[jobnum].weight
            if t_ready > deadline:
                twt += (t_ready - deadline) * weight

        return twt

    def _calc_loadbalance(self, assignment, makespan):
        """ Calculated the load balance for the machines in assignment.

        @param assignment: the machine assignment to calculate the load balance
        for.
        @type assignment: dict
        @param makespan: the makespan for the schedule. (For load
        normalization)
        @type makespan: number

        @return: the loadbalance value
        @rtype: number
        """
        # sum all production times for every machine
        m_prod_times = [0.0 for _ in enumerate(self.model.machine)]
        for op_id, assign in assignment.items():
            m_prod_times[assign[0]] +=\
                self.model.job[op_id[0]].operation[op_id[1]].op_duration
        for idx, time in enumerate(m_prod_times):
            m_prod_times[idx] = time/makespan
        # calculate the standard deviation
        return numpy.std(m_prod_times)

    def _calc_wip_and_flow(self, schedule):
        """ Calculates the maximum WIP (work in process) and the average flow factor.

        @param schedule: the schedule to calculate the WIP and flowfactor for.
        @type schedule: dict

        @return: 2 values: max wip, avg flowfactor
        @rtype: number, number
        """
        # create a list of all job start- and endtimes and their effects on the
        # WIP
        # use the start- and endtimes to calculate the flow factor for the job
        wip_changes = {}
        flowfactors = []
        for job_id, job in enumerate(self.model.job):
            last_op = len(job.operation) - 1
            jobstart = schedule[(job_id, 0)][1] - job.operation[0].op_duration
            jobend = schedule[(job_id, last_op)][1]
            lotsize = job.lotsize
            wip_changes[jobstart] = lotsize
            wip_changes[jobend] = -lotsize

            # calculate the raw processtime for the job
            ptime = sum([op.op_duration for op in job.operation])
            # store the passtimes
            flowfactors.append((jobend - jobstart) / ptime)

        # go through the wip changes in order and record the max occuring WIP
        max_wip = 0
        curr_wip = 0
        for _, change in sorted(wip_changes.items()):
            curr_wip += change
            if curr_wip > max_wip:
                max_wip = curr_wip

        return max_wip, numpy.average(flowfactors)
