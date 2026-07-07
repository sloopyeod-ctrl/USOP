from app.connectors.entra_connector import EntraConnector


class ConnectorService:
    def __init__(self):
        self.connectors = {
            "entra": EntraConnector(),
        }

    def list_connectors(self):
        return list(self.connectors.keys())

    def collect(self, connector_name: str):
        connector = self.connectors.get(connector_name)

        if connector is None:
            return None

        return connector.collect()

    def synchronize(self, connector_name: str):
        connector = self.connectors.get(connector_name)

        if connector is None:
            return None

        return connector.synchronize()