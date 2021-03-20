from src.core.Solution import Route
import logging


class CreateRoute:
    """
    this operator creates a new route
    """
    def __init__(self, **kwargs):
        self.solution = None

    def set_solution(self, solution):
        if not solution:
            logging.error(f"{self.__class__.__name__}::solution is undefined")
            exit(1)

        self.solution = solution

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


class InjectAfter:
    """
    this operator injects job b after job a
    """
    def __init__(self, **kwargs):
        self.solution = None

    def set_solution(self, solution):
        if not solution:
            logging.error(f"{self.__class__.__name__}::solution is undefined")
            exit(1)

        self.solution = solution

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


