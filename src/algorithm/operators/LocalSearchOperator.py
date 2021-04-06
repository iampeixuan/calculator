from src.core.Solution import Route
import logging


class LocalSearchOperator:
    def __init__(self, solution, **kwargs):
        if not solution:
            logging.error(f"{self.__class__.__name__}::solution is undefined")
            exit(1)
        else:
            self.solution = solution
            self.kwargs = kwargs

    def locate_job(self, job):
        for job_idx in range(len(self.solution.unassigned_jobs)):
            if self.solution.unassigned_jobs[job_idx] == job:
                return -1, job_idx

        for route_idx in range(len(self.solution.routes)):
            jobs = self.solution.routes[route_idx].jobs
            for job_idx in range(len(jobs)):
                if job == jobs[job_idx]:
                    return route_idx, job_idx

        logging.error(f"{self.__class__.__name__}::unable to locate job: {job}")
        return None, None

    def check_feasible(self):
        return self.solution.eval_constraint()

    def eval_and_check_feasible(self, allow_feasible=False):
        self.solution.eval_solution(allow_feasible)
        return self.solution.is_feasible


class CreateRoute(LocalSearchOperator):
    """
    this operator creates a new route
    """
    def __init__(self, solution, **kwargs):
        super().__init__(solution, **kwargs)
        self.route_idx = None
        self.job_idx = None
        self.last_job = None

    def move(self, vehicle_idx, job):
        logging.debug(f"{self.__class__.__name__}::trying to create route: vehicle {vehicle_idx}, job: {job}")

        self.last_job = job
        self.route_idx, self.job_idx = super().locate_job(job)

        if self.route_idx is not None:
            if self.route_idx == -1:
                self.solution.unassigned_jobs.pop(self.job_idx)
            elif self.route_idx > -1:
                self.solution.routes[self.route_idx].jobs.pop(self.job_idx)

            self.solution.routes.append(Route(vehicle_idx, [job]))

    def recover(self):
        if self.route_idx is not None:
            if self.route_idx == -1:
                self.solution.unassigned_jobs.insert(self.job_idx, self.last_job)
            elif self.route_idx > -1:
                self.solution.routes[self.route_idx].jobs.insert(self.job_idx, self.last_job)

            self.solution.routes.pop()


class InjectBefore(LocalSearchOperator):
    """
    this operator injects job b before job a
    """
    def __init__(self, solution, **kwargs):
        super().__init__(solution, **kwargs)
        self.route_idx_a = None
        self.job_idx_a = None
        self.last_a = None

        self.route_idx_b = None
        self.job_idx_b = None
        self.last_b = None

    def move(self, a, b):
        logging.debug(f"{self.__class__.__name__}::trying to inject job {b} before job {a}")
        if a == b:
            logging.error(f"{self.__class__.__name__}::two jobs are identical: {a}")
            exit(1)

        self.last_a = a
        self.last_b = b
        self.route_idx_a, self.job_idx_a = super().locate_job(a)
        self.route_idx_b, self.job_idx_b = super().locate_job(b)

        if self.route_idx_a is not None and self.route_idx_a > -1 and self.route_idx_b is not None:
            if self.route_idx_b == -1:
                self.solution.unassigned_jobs.pop(self.job_idx_b)
            elif self.route_idx_b > -1:
                self.solution.routes[self.route_idx_b].jobs.pop(self.job_idx_b)

            if self.route_idx_a != self.route_idx_b or self.job_idx_a < self.job_idx_b:
                self.solution.routes[self.route_idx_a].jobs.insert(self.job_idx_a, b)
            elif self.route_idx_a == self.route_idx_b and self.job_idx_a > self.job_idx_b:
                self.solution.routes[self.route_idx_a].jobs.insert(self.job_idx_a - 1, b)

    def recover(self):
        if self.route_idx_a is not None and self.route_idx_a > -1 and self.route_idx_b is not None:
            if self.route_idx_a != self.route_idx_b or self.job_idx_a < self.job_idx_b:
                self.solution.routes[self.route_idx_a].jobs.pop(self.job_idx_a)
            elif self.route_idx_a == self.route_idx_b and self.job_idx_a > self.job_idx_b:
                self.solution.routes[self.route_idx_a].jobs.pop(self.job_idx_a - 1)

            if self.route_idx_b == -1:
                self.solution.unassigned_jobs.insert(self.job_idx_b, self.last_b)
            elif self.route_idx_b > -1:
                self.solution.routes[self.route_idx_b].jobs.insert(self.job_idx_b, self.last_b)


class InjectAfter(LocalSearchOperator):
    """
    this operator injects job b after job a
    """
    def __init__(self, solution, **kwargs):
        super().__init__(solution, **kwargs)
        self.route_idx_a = None
        self.job_idx_a = None
        self.last_a = None

        self.route_idx_b = None
        self.job_idx_b = None
        self.last_b = None

    def move(self, a, b):
        logging.debug(f"{self.__class__.__name__}::trying to inject job {b} after job {a}")
        if a == b:
            logging.error(f"{self.__class__.__name__}::two jobs are identical: {a}")
            exit(1)

        self.last_a = a
        self.last_b = b
        self.route_idx_a, self.job_idx_a = super().locate_job(a)
        self.route_idx_b, self.job_idx_b = super().locate_job(b)

        if self.route_idx_a is not None and self.route_idx_a > -1 and self.route_idx_b is not None:
            if self.route_idx_b == -1:
                self.solution.unassigned_jobs.pop(self.job_idx_b)
            elif self.route_idx_b > -1:
                self.solution.routes[self.route_idx_b].jobs.pop(self.job_idx_b)

            if self.route_idx_a != self.route_idx_b or self.job_idx_a < self.job_idx_b:
                self.solution.routes[self.route_idx_a].jobs.insert(self.job_idx_a + 1, b)
            elif self.route_idx_a == self.route_idx_b and self.job_idx_a > self.job_idx_b:
                self.solution.routes[self.route_idx_a].jobs.insert(self.job_idx_a, b)

    def recover(self):
        if self.route_idx_a is not None and self.route_idx_a > -1 and self.route_idx_b is not None:
            if self.route_idx_a != self.route_idx_b or self.job_idx_a < self.job_idx_b:
                self.solution.routes[self.route_idx_a].jobs.pop(self.job_idx_a + 1)
            elif self.route_idx_a == self.route_idx_b and self.job_idx_a > self.job_idx_b:
                self.solution.routes[self.route_idx_a].jobs.pop(self.job_idx_a)

            if self.route_idx_b == -1:
                self.solution.unassigned_jobs.insert(self.job_idx_b, self.last_b)
            elif self.route_idx_b > -1:
                self.solution.routes[self.route_idx_b].jobs.insert(self.job_idx_b, self.last_b)


class TwoPoint(LocalSearchOperator):
    """
    this operator swaps the position of a and b
    """
    def __init__(self, solution, **kwargs):
        super().__init__(solution, **kwargs)
        self.route_idx_a = None
        self.job_idx_a = None
        self.last_a = None

        self.route_idx_b = None
        self.job_idx_b = None
        self.last_b = None

    def move(self, a, b):
        logging.debug(f"{self.__class__.__name__}::trying to swap job {a} and job {b}")
        if a == b:
            logging.error(f"{self.__class__.__name__}::two jobs are identical: {a}")
            exit(1)

        self.last_a = a
        self.last_b = b
        self.route_idx_a, self.job_idx_a = super().locate_job(a)
        self.route_idx_b, self.job_idx_b = super().locate_job(b)

        if self.route_idx_a is not None and self.route_idx_a > -1 and self.route_idx_b is not None and self.route_idx_b > -1:
            self.solution.routes[self.route_idx_a].jobs[self.job_idx_a] = b
            self.solution.routes[self.route_idx_b].jobs[self.job_idx_b] = a

    def recover(self):
        if self.route_idx_a is not None and self.route_idx_a > -1 and self.route_idx_b is not None and self.route_idx_b > -1:
            self.solution.routes[self.route_idx_a].jobs[self.job_idx_a] = self.last_a
            self.solution.routes[self.route_idx_b].jobs[self.job_idx_b] = self.last_b


class TwoOpt(LocalSearchOperator):
    """
    this operator does the following:
    - if a and b are in the same route: keep jobs before a, add jobs between a and b reversely, keep jobs after b
    - if a and b are in different routes: keep the jobs before a and b, swap the jobs after a and b between two routes
    """
    def __init__(self, solution, **kwargs):
        super().__init__(solution, **kwargs)
        self.route_idx_a = None
        self.job_idx_a = None
        self.last_route_a = None

        self.route_idx_b = None
        self.job_idx_b = None
        self.last_route_b = None

        self.moved = None

    def move(self, a, b):
        logging.debug(f"{self.__class__.__name__}::trying to 2-opt job {a} and job {b}")
        if a == b:
            logging.error(f"{self.__class__.__name__}::two jobs are identical: {a}")
            exit(1)

        self.moved = False
        self.route_idx_a, self.job_idx_a = super().locate_job(a)
        self.route_idx_b, self.job_idx_b = super().locate_job(b)
        self.last_route_a = self.solution.routes[self.route_idx_a].copy()
        self.last_route_b = self.solution.routes[self.route_idx_b].copy()

        a_is_end = self.job_idx_a == len(self.solution.routes[self.route_idx_a].jobs) - 1
        b_is_end = self.job_idx_b == len(self.solution.routes[self.route_idx_b].jobs) - 1
        if a_is_end and b_is_end:
            return

        if self.route_idx_a is not None and self.route_idx_a > -1 and self.route_idx_b is not None and self.route_idx_b > -1:
            if self.route_idx_a == self.route_idx_b:
                start = min(self.job_idx_a, self.job_idx_b)
                end = max(self.job_idx_a, self.job_idx_b)
                jobs = self.solution.routes[self.route_idx_a].jobs
                self.solution.routes[self.route_idx_a].jobs = jobs[:start] + jobs[start:end+1][::-1] + jobs[end+1:]
                self.moved = True
            else:
                jobs_a = self.solution.routes[self.route_idx_a].jobs
                jobs_b = self.solution.routes[self.route_idx_b].jobs
                updated_jobs_a = jobs_a[:self.job_idx_a+1] + jobs_b[self.job_idx_b+1:]
                updated_jobs_b = jobs_b[:self.job_idx_b+1] + jobs_a[self.job_idx_a+1:]
                self.solution.routes[self.route_idx_a].jobs = updated_jobs_a
                self.solution.routes[self.route_idx_b].jobs = updated_jobs_b
                self.moved = True

    def recover(self):
        if not self.moved:
            return

        if self.route_idx_a is not None and self.route_idx_a > -1 and self.route_idx_b is not None and self.route_idx_b > -1:
            self.solution.routes[self.route_idx_a] = self.last_route_a
            self.solution.routes[self.route_idx_b] = self.last_route_b
