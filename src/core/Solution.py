import logging


class Route:
    def __init__(self, vehicle_idx=-1, jobs=[]):
        self.vehicle_idx = vehicle_idx
        self.jobs = jobs

    def copy(self):
        return Route(self.vehicle_idx, [job for job in self.jobs])

    def clear_jobs(self):
        self.jobs = []

    def __repr__(self):
        return f"vehicle_idx: {self.vehicle_idx}, jobs: {self.jobs}"


class Solution:
    def __init__(self, problem):
        self.problem = problem
        self.routes = []
        self.unassigned_jobs = []
        self.objectives_output = []
        self.is_feasible = True
        self.cache = None

    def create_cache(self):
        self.cache = self.copy()
        return self.cache

    def reset_cache(self):
        self.cache.assigned_by(self)

    def accept_cache(self):
        if self.cache:
            self.assigned_by(self.cache)
        else:
            logging.warning(f"{self.__class__.__name__}::cache is not defined, creating a copy of solution as cache")
            self.create_cache()

    def copy(self):
        solution = Solution(self.problem)
        solution.routes = [route.copy() for route in self.routes]
        solution.unassigned_jobs = [job for job in self.unassigned_jobs]
        solution.objectives_output = [output for output in self.objectives_output]
        solution.is_feasible = self.is_feasible

        return solution

    def assigned_by(self, other):
        self.routes = [route.copy() for route in other.routes]
        self.unassigned_jobs = [job for job in other.unassigned_jobs]
        self.objectives_output = [output for output in other.objectives_output]
        self.is_feasible = other.is_feasible

    def get_route(self, vehicle_idx):
        for route in self.routes:
            if route.vehicle_idx == vehicle_idx:
                return route

    def set_unassigned_jobs(self, unassigned_jobs):
        self.unassigned_jobs = unassigned_jobs

    def eval_unassigned_jobs(self):
        assigned_jobs = [job for route in self.routes for job in route.jobs]
        unassigned_jobs = [job for job in self.problem.job_indexes if job not in assigned_jobs]
        self.set_unassigned_jobs(unassigned_jobs)

        return len(self.unassigned_jobs)

    def eval_constraint(self):
        self.is_feasible = True
        for constraint in self.problem.model.constraints:
            if not constraint(self):
                self.is_feasible = False
                break

        return self.is_feasible

    def eval_objective(self):
        self.objectives_output = [objective.function(self) for objective in self.problem.model.objectives]

        return self.objectives_output

    def eval_solution(self, allow_infeasible=False):
        self.eval_unassigned_jobs()
        if self.eval_constraint() or allow_infeasible:
            self.eval_objective()

    def equals(self, other):
        self_routes = [route.jobs for route in self.routes]
        other_routes = [route.jobs for route in other.routes]
        for route in self_routes:
            if route not in other_routes:
                return False

        return True

    def __eq__(self, other):
        for i in range(len(self.objectives_output)):
            if self.objectives_output[i] != other.objectives_output[i]:
                return False

        return True

    def __lt__(self, other):
        for i in range(len(self.objectives_output)):
            if self.objectives_output[i] < other.objectives_output[i]:
                return True

        return False

    def __gt__(self, other):
        for i in range(len(self.objectives_output)):
            if self.objectives_output[i] > other.objectives_output[i]:
                return True

        return False

    def __repr__(self):
        names = [objective.name for objective in self.problem.model.objectives]
        return f"is_feasible: {self.is_feasible}, num_unassigned_jobs: {len(self.unassigned_jobs)}, objectives: {list(zip(names, self.objectives_output))}"
