class EnergyGrid:
    class GridNode:
        def __init__(self, label: str, node_id: int, power: int):
            self.label = label
            self.node_id = node_id
            self.power = power
            self.is_producer = power > 0

        def __str__(self):
            if self.is_producer:
                return f"Node(label={self.label}, id={self.node_id}, role=Producer, outputs={self.power})"
            else:
                return f"Node(label={self.label}, id={self.node_id}, role=Consumer, requests={-self.power})"

        def __repr__(self):
            return self.__str__()

        @staticmethod
        def parse(line):
            node_id, label, power = line.split(" ")
            return EnergyGrid.GridNode(label, int(node_id), int(power))

    class GridLink:
        def __init__(self, from_: int, to_: int, capacity: int):
            self.from_ = from_
            self.to_ = to_
            self.capacity = capacity

        def __str__(self):
            return f"Edge(from={self.from_}, to={self.to_}, capacity={self.capacity})"

        def __repr__(self):
            return self.__str__()

        @staticmethod
        def parse(line):
            from_, to_, capacity = line.split(" ")
            return EnergyGrid.GridLink(int(from_), int(to_), int(capacity))

    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges

    def get_adjacent_nodes(self, node):
        adjacent = []
        for edge in self.edges:
            if edge.from_ == node:
                adjacent.append((edge.to_, edge.capacity))
            if edge.to_ == node:
                adjacent.append((edge.from_, edge.capacity))
        return adjacent

    class ReadingState:
        INITIAL = 0
        READING_NODES = 1
        READING_LINKS = 2

    @staticmethod
    def parse(file_contents):
        state = EnergyGrid.ReadingState.INITIAL
        nodes = {}
        edges = []

        for line in file_contents.splitlines():
            if line == "nodes":
                state = EnergyGrid.ReadingState.READING_NODES
            elif line == "links":
                state = EnergyGrid.ReadingState.READING_LINKS
            else:
                match state:
                    case EnergyGrid.ReadingState.INITIAL:
                        raise "first line of grid spec should be \"nodes\""
                    case EnergyGrid.ReadingState.READING_NODES:
                        node = EnergyGrid.GridNode.parse(line)
                        nodes[node.node_id] = node
                    case EnergyGrid.ReadingState.READING_LINKS:
                        edges.append(EnergyGrid.GridLink.parse(line))

        return EnergyGrid(nodes, edges)

    @staticmethod
    def load_energy_grid(filename):
        with open(filename) as input_file:
            return EnergyGrid.parse(input_file.read())
