from dataclasses import dataclass
from typing import Any


@dataclass(
    frozen=True,
    slots=True,
)
class DecisionDraftEvidence:
    """
    One authoritative source supporting a deterministic draft segment.

    Evidence references identify why text was constructed. They do not
    authorize a decision, interpret policy, or independently prescribe an
    organizational response.
    """

    source_type: str
    label: str
    source_id: str | None = None
    detail: str | None = None

    def __post_init__(self):
        self._require_text(
            self.source_type,
            "Evidence source type",
        )
        self._require_text(
            self.label,
            "Evidence label",
        )

    def identity_key(
        self,
    ) -> tuple[
        str,
        str | None,
        str,
    ]:
        """
        Return the stable identity used for evidence deduplication.
        """

        return (
            self.source_type,
            self.source_id,
            self.label,
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "source_type": self.source_type,
            "source_id": self.source_id,
            "label": self.label,
            "detail": self.detail,
        }

    @staticmethod
    def _require_text(
        value: str,
        field_name: str,
    ) -> None:
        if (
            not isinstance(value, str)
            or not value.strip()
        ):
            raise ValueError(
                f"{field_name} is required."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class DecisionDraftSegment:
    """
    One explainable unit of deterministic draft text.

    A segment may be used in either the suggested justification or suggested
    analyst notes. Every segment must contain at least one evidence reference.
    """

    text: str
    evidence: tuple[
        DecisionDraftEvidence,
        ...,
    ]

    def __post_init__(self):
        if (
            not isinstance(self.text, str)
            or not self.text.strip()
        ):
            raise ValueError(
                "Draft segment text is required."
            )

        if not self.evidence:
            raise ValueError(
                "Draft segment evidence is required."
            )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "text": self.text,
            "evidence": [
                item.to_dict()
                for item in self.evidence
            ],
        }


@dataclass(
    frozen=True,
    slots=True,
)
class DecisionDraft:
    """
    Deterministic documentation draft for a decision chosen by an analyst.

    DecisionDraft never selects a decision type. It only constructs
    explainable documentation after the analyst or calling workflow supplies
    the intended decision type.

    The analyst remains responsible for reviewing, editing, and submitting
    the final organizational decision.
    """

    decision_type: str

    justification_segments: tuple[
        DecisionDraftSegment,
        ...,
    ]

    notes_segments: tuple[
        DecisionDraftSegment,
        ...,
    ]

    confidence_score: int

    construction_version: str = (
        "decision-draft-v1"
    )

    def __post_init__(self):
        if (
            not isinstance(
                self.decision_type,
                str,
            )
            or not self.decision_type.strip()
        ):
            raise ValueError(
                "Decision type is required."
            )

        if not (
            0
            <= self.confidence_score
            <= 100
        ):
            raise ValueError(
                "Draft confidence score must "
                "be between 0 and 100."
            )

        if (
            not isinstance(
                self.construction_version,
                str,
            )
            or not self.construction_version.strip()
        ):
            raise ValueError(
                "Construction version is required."
            )

    @property
    def suggested_justification(
        self,
    ) -> str:
        """
        Return analyst-ready justification assembled in segment order.
        """

        return " ".join(
            segment.text.strip()
            for segment
            in self.justification_segments
        )

    @property
    def suggested_notes(
        self,
    ) -> str:
        """
        Return analyst-ready notes assembled in segment order.
        """

        return "\n".join(
            segment.text.strip()
            for segment
            in self.notes_segments
        )

    @property
    def evidence_used(
        self,
    ) -> tuple[
        DecisionDraftEvidence,
        ...,
    ]:
        """
        Return stable, first-seen evidence without duplicates.
        """

        ordered_evidence: list[
            DecisionDraftEvidence
        ] = []

        seen_keys: set[
            tuple[
                str,
                str | None,
                str,
            ]
        ] = set()

        all_segments = (
            self.justification_segments
            + self.notes_segments
        )

        for segment in all_segments:
            for evidence in segment.evidence:
                key = evidence.identity_key()

                if key in seen_keys:
                    continue

                seen_keys.add(key)
                ordered_evidence.append(
                    evidence
                )

        return tuple(
            ordered_evidence
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Return a transport-safe projection without exposing dataclasses.
        """

        return {
            "decision_type": (
                self.decision_type
            ),
            "suggested_justification": (
                self.suggested_justification
            ),
            "suggested_notes": (
                self.suggested_notes
            ),
            "justification_segments": [
                segment.to_dict()
                for segment
                in self.justification_segments
            ],
            "notes_segments": [
                segment.to_dict()
                for segment
                in self.notes_segments
            ],
            "evidence_used": [
                evidence.to_dict()
                for evidence
                in self.evidence_used
            ],
            "confidence_score": (
                self.confidence_score
            ),
            "construction_version": (
                self.construction_version
            ),
        }
