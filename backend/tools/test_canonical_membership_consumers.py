import sys
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(
    0,
    str(BACKEND_ROOT),
)

load_dotenv(
    dotenv_path=BACKEND_ROOT / ".env",
    override=False,
)

from app.analytics.access_analyzer import AccessAnalyzer
from app.database.session import SessionLocal
from app.governance.snapshot_builder import SnapshotBuilder
from app.graph.identity_graph_service import IdentityGraphService
from app.intelligence.attack_path_service import AttackPathService
from app.intelligence.executive_exposure_dashboard_service import (
    ExecutiveExposureDashboardService,
)
from app.intelligence.identity_intelligence_service import (
    IdentityIntelligenceService,
)
from app.services.access_summary_service import (
    AccessSummaryService,
)


IDENTITY_ID = "da6ea20f-f3d0-4596-b7a1-021202da549e"


def main() -> int:
    print("USOP Canonical Membership Consumer Regression")
    print("---------------------------------------------")

    db = SessionLocal()

    try:
        analyzer = AccessAnalyzer(db)

        privileged_identities = (
            analyzer.privileged_identities()
        )
        identity_risks = analyzer.identity_risk()

        graph = IdentityGraphService(
            db
        ).get_identity_graph(
            IDENTITY_ID
        )

        intelligence = IdentityIntelligenceService(
            db
        ).get_identity_intelligence(
            IDENTITY_ID
        )

        attack_path = AttackPathService(
            db
        ).get_attack_path(
            IDENTITY_ID
        )

        dashboard = ExecutiveExposureDashboardService(
            db
        ).dashboard()

        access_summary = AccessSummaryService(
            db
        ).get_identity_access_summary(
            IDENTITY_ID
        )

        snapshot = SnapshotBuilder(
            db
        ).build(
            IDENTITY_ID
        )

        errors = []

        if graph is None:
            errors.append(
                "Identity graph returned no result."
            )

        if intelligence is None:
            errors.append(
                "Identity intelligence returned no result."
            )

        if attack_path is None:
            errors.append(
                "Attack path returned no result."
            )

        if access_summary is None:
            errors.append(
                "Access summary returned no result."
            )

        if not snapshot:
            errors.append(
                "Snapshot builder returned no result."
            )

        if dashboard is None:
            errors.append(
                "Executive dashboard returned no result."
            )

        if not isinstance(
            privileged_identities,
            list,
        ):
            errors.append(
                "Privileged identity analysis did not "
                "return a list."
            )

        if not isinstance(
            identity_risks,
            list,
        ):
            errors.append(
                "Identity risk analysis did not return "
                "a list."
            )

        if errors:
            print()
            print("Validation: FAILED")

            for error in errors:
                print(f"- {error}")

            return 1

        print(
            "Identity: "
            f"{graph['identity']['display_name']}"
        )
        print(
            "Graph accounts: "
            f"{len(graph['accounts'])}"
        )
        print(
            "Graph groups: "
            f"{len(graph['groups'])}"
        )
        print(
            "Graph roles: "
            f"{len(graph['roles'])}"
        )
        print(
            "Risk records: "
            f"{len(identity_risks)}"
        )
        print(
            "Privileged identity records: "
            f"{len(privileged_identities)}"
        )
        print(
            "Recommendations: "
            f"{len(intelligence['recommendations'])}"
        )
        print(
            "Attack-path nodes: "
            f"{len(attack_path['attack_path']['nodes'])}"
        )
        print(
            "Attack-path edges: "
            f"{len(attack_path['attack_path']['edges'])}"
        )
        print(
            "Dashboard identities: "
            f"{dashboard['summary']['total_identities']}"
        )
        print(
            "Access-summary groups: "
            f"{len(access_summary['groups'])}"
        )
        print(
            "Access-summary roles: "
            f"{len(access_summary['roles'])}"
        )
        print(
            "Snapshot groups: "
            f"{len(snapshot['groups'])}"
        )
        print(
            "Snapshot roles: "
            f"{len(snapshot['roles'])}"
        )

        print()
        print("Validation: PASSED")
        print(
            "Analytics, governance, and access-summary "
            "consumers now use canonical membership "
            "relationships."
        )

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
