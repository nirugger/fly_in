class Manager:

    def __init__(
            self,
            graph: Graph,
            drones: list[Drone],
            turn: int,):
        
    graph: Graph
    drones: list[Drone]
    turn: int
    history: list[list[str]]
    _paths: dict[int, list[Zone]]   # drone_id -> path, gestito internamente

    def run(self) -> None: ...
    def get_graph_status(self) -> GraphStatus: ...  # snapshot passivo
    def _recompute_paths(self, status: GraphStatus) -> None: ...
    def compute_turn(self) -> list[str]: ...        # plan → verify → execute
    def all_arrived(self) -> bool: ...