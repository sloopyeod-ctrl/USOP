from app.connectors.base import BaseConnector


class EntraConnector(BaseConnector):
    def collect(self):
        return {
            "identities": [
                {
                    "display_name": "Marvin Dewitt",
                    "primary_email": "mgeoffdewitt@gmail.com",
                }
            ],
            "accounts": [
                {
                    "username": "mdewitt",
                    "system_name": "Entra ID",
                }
            ],
            "groups": [
                {
                    "name": "entra-security-admins",
                }
            ],
            "roles": [
                {
                    "name": "Global Reader",
                }
            ],
        }

    def synchronize(self):
        data = self.collect()

        return {
            "connector": "Entra ID",
            "status": "success",
            "objects": {
                "identities": len(data["identities"]),
                "accounts": len(data["accounts"]),
                "groups": len(data["groups"]),
                "roles": len(data["roles"]),
            },
        }