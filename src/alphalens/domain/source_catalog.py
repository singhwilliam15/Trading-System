"""Canonical source metadata for supplied AlphaLens research inputs."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SourceKind(StrEnum):
    DOCUMENT = "document"
    WORKBOOK = "workbook"


@dataclass(frozen=True, slots=True)
class SourceDefinition:
    """Describes a required, externally supplied research artifact."""

    filename: str
    kind: SourceKind
    purpose: str


SOURCE_CATALOG: tuple[SourceDefinition, ...] = (
    SourceDefinition("DalalStreet_Elite_Strategy_Report.docx", SourceKind.DOCUMENT, "strategy research"),
    SourceDefinition("Enhanced_Final_Report.docx", SourceKind.DOCUMENT, "integrated strategy research"),
    SourceDefinition("Full_Strategy_Report.docx", SourceKind.DOCUMENT, "full strategy reference"),
    SourceDefinition("Phase_1_Market_Understanding.docx", SourceKind.DOCUMENT, "market understanding"),
    SourceDefinition("Phase_2_Asset_Class_Analysis.docx", SourceKind.DOCUMENT, "asset-class analysis"),
    SourceDefinition("Phase_3_Investor_Strategy.docx", SourceKind.DOCUMENT, "investor strategy"),
    SourceDefinition("Phase_4_Trader_Strategy.docx", SourceKind.DOCUMENT, "trader strategy"),
    SourceDefinition("Phase_5_Derivatives_Strategies.docx", SourceKind.DOCUMENT, "derivatives strategy"),
    SourceDefinition("BS-FIRST PRINCIPLE-STUDENT.xlsx", SourceKind.WORKBOOK, "risk-management principles"),
    SourceDefinition("VaR_Risk_Management_Tool.xlsx", SourceKind.WORKBOOK, "value-at-risk model"),
)
"""Canonical source metadata for supplied AlphaLens research inputs."""
