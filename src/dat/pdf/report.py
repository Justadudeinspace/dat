"""PDF export utilities for DAT reports."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table

from ..scanner.core import FileReport, ScanReport


def _document(report: ScanReport) -> Iterable:
    styles = getSampleStyleSheet()
    heading = styles["Heading1"]
    normal = styles["BodyText"]

    yield Paragraph("Dev Audit Tool Report", heading)
    yield Paragraph(f"Repository: {report.repo}", normal)
    yield Paragraph(f"Root: {report.root}", normal)
    yield Paragraph(f"Generated: {datetime.utcnow().isoformat()}Z", normal)
    if report.metadata:
        for key, value in report.metadata.items():
            yield Paragraph(f"{key.title()}: {value}", normal)
    yield Spacer(1, 12)

    table_data = [["Path", "Size", "Checksum", "Issues"]]
    for file_report in report.files:
        issue_count = len(file_report.violations)
        table_data.append(
            [
                file_report.path,
                str(file_report.size),
                file_report.checksum[:12] + "…",
                str(issue_count),
            ]
        )
    yield Table(table_data, repeatRows=1)


def export_pdf(report: ScanReport, destination: Path) -> Path:
    """Write *report* into *destination* as a PDF document."""

    doc = SimpleDocTemplate(str(destination), pagesize=letter)
    doc.build(list(_document(report)))
    return destination
