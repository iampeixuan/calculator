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


class CreateRoute(LocalSearchOperator):
    """
    this operator creates a new route
    """
    def create(self, vehicle_idx, jobs):
        logging.debug(f"{self.__class__.__name__}::trying to create route: vehicle {vehicle_idx}, jobs: {jobs}")
        for job in jobs:
            if job in self.solution.unassigned_jobs:
                self.solution.unassigned_jobs.remove(job)
            else:
                for route in self.solution.routes:
                    if job in route.jobs:
                        route.jobs.remove(job)
                        break

        self.solution.routes.append(Route(vehicle_idx, jobs))


class InjectBefore(LocalSearchOperator):
    """
    this operator injects job b before job a
    """
    def move(self, a, b):
        logging.debug(f"{self.__class__.__name__}::trying to inject job {b} before job {a}")
        # remove b from unassigned jobs or the other route
        if b in self.solution.unassigned_jobs:
            self.solution.unassigned_jobs.remove(b)
        else:
            for route in self.solution.routes:
                if b in route.jobs:
                    route.jobs.remove(b)
                    break

        # insert b to the index at a
        for route in self.solution.routes:
            for index, job in enumerate(route.jobs):
                if job == a:
                    route.jobs.insert(index, b)
                    break


class InjectAfter(LocalSearchOperator):
    """
    this operator injects job b after job a
    """
    def move(self, a, b):
        logging.debug(f"{self.__class__.__name__}::trying to inject job {b} after job {a}")
        # remove b from unassigned jobs or the other route
        if b in self.solution.unassigned_jobs:
            self.solution.unassigned_jobs.remove(b)
        else:
            for route in self.solution.routes:
                if b in route.jobs:
                    route.jobs.remove(b)
                    break

        # insert b to the index after a
        for route in self.solution.routes:
            for index, job in enumerate(route.jobs):
                if job == a:
                    route.jobs.insert(index + 1, b)
                    break


class TwoPoint(LocalSearchOperator):
    """
    this operator swaps the position of a and b
    """
    def move(self, a, b):
        logging.debug(f"{self.__class__.__name__}::trying to swap job {a} and job {b}")
        if a == b:
            return

        route_index_a = None
        route_index_b = None
        job_index_a = None
        job_index_b = None

        for route_index, route in enumerate(self.solution.routes):
            for job_index, job in enumerate(route.jobs):
                if route_index_a is not None and route_index_b is not None:
                    break
                if job == a:
                    route_index_a = route_index
                    job_index_a = job_index
                if job == b:
                    route_index_b = route_index
                    job_index_b = job_index

        self.solution.routes[route_index_a].jobs[job_index_a] = b
        self.solution.routes[route_index_b].jobs[job_index_b] = a


class TwoOpt(LocalSearchOperator):
    """
    this operator does the following:
    - if a and b are in the same route: keep jobs before a, add jobs between a and b reversely, keep jobs after b
    - if a and b are in different routes: keep the jobs before a and b, swap the jobs after a and b between two routes
    """
    def move(self, a, b):
        logging.debug(f"{self.__class__.__name__}::trying to swap job {a} and job {b}")
        if a == b:
            return

        route_index_a = None
        route_index_b = None
        job_index_a = None
        job_index_b = None
        a_is_end = None
        b_is_end = None

        for route_index, route in enumerate(self.solution.routes):
            for job_index, job in enumerate(route.jobs):
                if route_index_a is not None and route_index_b is not None:
                    break
                if job == a:
                    route_index_a = route_index
                    job_index_a = job_index
                    a_is_end = job_index_a == len(route.jobs) - 1
                if job == b:
                    route_index_b = route_index
                    job_index_b = job_index
                    b_is_end = job_index_b == len(route.jobs) - 1

        if a_is_end and b_is_end:
            return

        if route_index_a == route_index_b:
            start = min(job_index_a, job_index_b)
            end = max(job_index_a, job_index_b)
            jobs = self.solution.routes[route_index_a].jobs
            self.solution.routes[route_index_a].jobs = jobs[:start] + jobs[start:end+1][::-1] + jobs[end+1:]
        else:
            jobs_a = self.solution.routes[route_index_a].jobs
            jobs_b = self.solution.routes[route_index_b].jobs
            updated_jobs_a = jobs_a[:job_index_a+1] + jobs_b[job_index_b+1:]
            updated_jobs_b = jobs_b[:job_index_b+1] + jobs_a[job_index_a+1:]
            self.solution.routes[route_index_a].jobs = updated_jobs_a
            self.solution.routes[route_index_b].jobs = updated_jobs_b
