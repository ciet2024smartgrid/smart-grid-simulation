import numpy as np
from energy_grid import EnergyGrid

class Solution:
    def __init__(self, satisfied, transfers, energy_grid):
        self.satisfied = satisfied
        self.transfers = transfers
        self.energy_grid = energy_grid

    def print(self):
        for node_id in self.satisfied:
            node = self.energy_grid.nodes[node_id]
            supply = self.satisfied[node_id]

            if node.is_producer:
                print(f"Node \"{node.label}\" output {supply}/{abs(node.power)} power")
            else:
                print(f"Node \"{node.label}\" received {supply}/{abs(node.power)} power")

        for (from_, to_, supply, capacity) in self.transfers:
            from_label = self.energy_grid.nodes[from_].label
            to_label = self.energy_grid.nodes[to_].label
            print(f"Transferred {supply}/{capacity} from {from_label} to {to_label}")


def bfs_priority(energy_grid):
    bfs_queue = []
    visited = set()

    for node_id in energy_grid.nodes:
        if energy_grid.nodes[node_id].is_producer:
            bfs_queue.append((node_id, 0))

    priority = []

    while len(bfs_queue) > 0:
        node_id, distance = bfs_queue.pop(0)
        if node_id not in visited:
            visited.add(node_id)
            if distance > 0:
                priority.append(node_id)
            for (neighbour, _) in energy_grid.get_adjacent_nodes(node_id):
                bfs_queue.append((neighbour, distance + 1))

    priority.reverse()
    return priority


def bfs_augmenting_path(energy_grid, root, flow_matrix, satisfied):
    assert not energy_grid.nodes[root].is_producer
    root_node_request = abs(energy_grid.nodes[root].power) - satisfied.get(root, 0)
    bfs_queue = [(root, root_node_request, None)]
    visited = set()
    predecessor = {}

    while len(bfs_queue) > 0:
        node_id, path_capacity, parent = bfs_queue.pop(0)
        if node_id is not None:
            if node_id not in visited:
                visited.add(node_id)
                if parent is not None:
                    predecessor[node_id] = parent

                for (neighbour, edge_capacity) in energy_grid.get_adjacent_nodes(node_id):
                    effective_link_capacity = edge_capacity - flow_matrix[neighbour, node_id]
                    assert 0 <= effective_link_capacity <= 2 * edge_capacity
                    new_path_capacity = min(effective_link_capacity, path_capacity)
                    if new_path_capacity > 0:
                        bfs_queue.append((neighbour, new_path_capacity, node_id))

                node = energy_grid.nodes[node_id]
                if node.is_producer:
                    effective_supply = node.power - satisfied.get(node_id, 0)
                    assert 0 <= effective_supply <= node.power
                    new_path_capacity = min(effective_supply, path_capacity)
                    if new_path_capacity > 0:
                        bfs_queue.append((None, new_path_capacity, node_id))
        else:
            path = []
            current_node = parent
            path.append(current_node)
            while current_node in predecessor:
                pred = predecessor[current_node]
                path.append(pred)
                current_node = pred
            path.reverse()
            assert path[0] == root
            return path, path_capacity


def find_next_augmenting_path(energy_grid, consumer_priorities, flow_matrix, satisfied):
    while len(consumer_priorities) > 0:
        highest_priority = consumer_priorities.pop()
        path = bfs_augmenting_path(energy_grid, highest_priority, flow_matrix, satisfied)
        if path is not None:
            consumer_priorities.append(highest_priority)
            return path
        else:
            continue


def resolve_energy_grid(energy_grid: EnergyGrid, priority="closest") -> Solution:
    match priority:
        case "closest":
            consumer_priorities = bfs_priority(energy_grid)
        case _:
            raise "unrecognised priority method"

    number_of_nodes = len(energy_grid.nodes)
    flow_matrix = np.zeros((number_of_nodes, number_of_nodes), dtype=np.int64)

    satisfied = {node_id: 0 for node_id in energy_grid.nodes}

    while (path := find_next_augmenting_path(energy_grid,
                                             consumer_priorities,
                                             flow_matrix,
                                             satisfied)) is not None:
        path, path_capacity = path

        edge_start = path.pop()
        satisfied[edge_start] += path_capacity

        while len(path) > 0:
            edge_end = path.pop()
            flow_matrix[edge_start, edge_end] += path_capacity
            flow_matrix[edge_end, edge_start] -= path_capacity

            edge_start = edge_end

        satisfied[edge_start] += path_capacity

    transfers = []

    for edge in energy_grid.edges:
        flow_along_edge = flow_matrix[edge.from_, edge.to_]

        if flow_along_edge > 0:
            transfers.append((edge.from_, edge.to_, flow_along_edge, edge.capacity))
        if flow_along_edge < 0:
            transfers.append((edge.to_, edge.from_, flow_along_edge, edge.capacity))

    return Solution(satisfied, transfers, energy_grid)
