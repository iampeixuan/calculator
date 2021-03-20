class Attr:
    def __init__(self, name, index):
        self.name = name
        self.index = index


class GlobalAttr(Attr):
    def __init__(self, name, index):
        Attr.__init__(self, name, index)


class NodeAttr(Attr):
    def __init__(self, name, index):
        Attr.__init__(self, name, index)


class VehicleAttr(Attr):
    def __init__(self, name, index):
        Attr.__init__(self, name, index)


class NodeNodeAttr(Attr):
    def __init__(self, name, index):
        Attr.__init__(self, name, index)


class VehicleNodeNodeAttr(Attr):
    def __init__(self, name, index):
        Attr.__init__(self, name, index)


class Objective:
    def __init__(self, function, name="Objective"):
        self.function = function
        self.name = name


class Model:
    def __init__(self):
        self.global_attrs = []
        self.vehicle_attrs = []
        self.node_attrs = []
        self.node_node_attrs = []
        self.vehicle_node_node_attrs = []

    def create(self):
        for name in self.global_attributes:
            setattr(self, name, self.define_global_attr(name))

        for name in self.vehicle_attributes:
            setattr(self, name, self.define_vehicle_attr(name))

        for name in self.node_attributes:
            setattr(self, name, self.define_node_attr(name))

        for name in self.node_node_attributes:
            setattr(self, name, self.define_node_node_attr(name))

        for name in self.vehicle_node_node_attributes:
            setattr(self, name, self.define_vehicle_node_node_attr(name))

        return self

    def define_global_attr(self, attr_name):
        attr = GlobalAttr(attr_name, len(self.global_attrs))
        self.global_attrs.append(attr)
        return attr

    def define_vehicle_attr(self, attr_name):
        attr = VehicleAttr(attr_name, len(self.vehicle_attrs))
        self.vehicle_attrs.append(attr)
        return attr

    def define_node_attr(self, attr_name):
        attr = NodeAttr(attr_name, len(self.node_attrs))
        self.node_attrs.append(attr)
        return attr

    def define_node_node_attr(self, attr_name):
        attr = NodeNodeAttr(attr_name, len(self.node_node_attrs))
        self.node_node_attrs.append(attr)
        return attr

    def define_vehicle_node_node_attr(self, attr_name):
        attr = VehicleNodeNodeAttr(attr_name, len(self.vehicle_node_node_attrs))
        self.vehicle_node_node_attrs.append(attr)
        return attr

