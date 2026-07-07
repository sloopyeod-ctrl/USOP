from copy import deepcopy

from app.graph.identity_graph_service import IdentityGraphService


class GraphSnapshotService:
    def __init__(self, db):
        self.graph_service = IdentityGraphService(db)

    def snapshot_identity(self, identity_id: str):
        graph = self.graph_service.get_identity_graph(identity_id)

        if graph is None:
            return None

        return deepcopy(graph)