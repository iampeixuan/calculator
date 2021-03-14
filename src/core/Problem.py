import logging


class Problem:
    def __init__(self, model, depot_indexes, global_attrs, vehicles_with_attrs, nodes_with_attrs, node_node_attrs, vehicle_node_node_attrs):
        self.model = model
        self.closeness = None
        self.neighbour_array = None

        self.num_vehicles = len(vehicles_with_attrs)
        self.num_nodes = len(nodes_with_attrs)
        self.depot_index_list = depot_indexes
        self.job_indexes = list(range(len(depot_indexes), self.num_nodes))

        self.global_attrs_tensor = [global_attrs[attr.name] for attr in self.model.global_attrs]
        self.vehicle_attrs_tensor = [[vehicle_attrs[attr.name] for attr in self.model.vehicle_attrs] for vehicle_attrs in vehicles_with_attrs]
        self.node_attrs_tensor = [[node_attrs[attr.name] for attr in self.model.node_attrs] for node_attrs in nodes_with_attrs]
        self.node_node_attrs_tensor = [[[node_node_attrs[attr.name][x][y] for attr in self.model.node_node_attrs] for y in range(self.num_nodes)] for x in range(self.num_nodes)]
        self.vehicle_node_node_attr_tensor = [[[[vehicle_node_node_attrs[attr.name][v][x][y] for attr in self.model.vehicle_node_node_attrs] for y in range(self.num_nodes)] for x in range(self.num_nodes)] for v in range(self.num_vehicles)]

        logging.info(f"{self.__class__.__name__}::num of vehicles in problem: {self.num_vehicles}")
        logging.info(f"{self.__class__.__name__}::num of nodes in problem: {self.num_nodes}")

    def get_global_attr(self, attr):
        return self.global_attrs_tensor[attr.index]

    def get_vehicle_attr(self, vehicle_idx, attr):
        return self.vehicle_attrs_tensor[vehicle_idx][attr.index]

    def get_node_attr(self, node_idx, attr):
        return self.node_attrs_tensor[node_idx][attr.index]

    def get_node_node_attr(self, node_idx1, node_idx2, attr):
        return self.node_node_attrs_tensor[node_idx1][node_idx2][attr.index]

    def get_vehicle_node_node_attr(self, vehicle_idx, node_idx1, node_idx2, attr):
        return self.vehicle_node_node_attr_tensor[vehicle_idx][node_idx1][node_idx2][attr.index]

    def set_closeness(self, closeness):
        self.closeness = closeness

    def update_neighbour(self, neighbourhood_size):
        if self.closeness is not None:
            logging.info(f"{self.__class__.__name__}::updating neighbourhood with size: {neighbourhood_size}")
            self.neighbour_array = []
            for node_idx in range(self.num_nodes):
                cost_to_neighbour = []
                for neighbour_idx in range(self.num_nodes):
                    if node_idx != neighbour_idx:
                        cost_to_neighbour.append((self.closeness(self, node_idx, neighbour_idx), neighbour_idx))

                cost_to_neighbour.sort(key=lambda x: x[0])
                neighbours = [cost[1] for cost in cost_to_neighbour]
                if neighbourhood_size >= len(neighbours):
                    self.neighbour_array.append(neighbours)
                else:
                    self.neighbour_array.append(neighbours[:neighbourhood_size])
        else:
            logging.error(f"{self.__class__.__name__}::closeness is not defined for the problem")
            exit(1)
