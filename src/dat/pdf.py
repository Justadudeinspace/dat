"""PDF report writer using ReportLab."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from .rules import RuleFinding
from .scanner import ScanResult

MONO_FONTS = [
    ("DejaVuSansMono", "DejaVuSansMono.ttf"),
    ("Courier", "courier"),
]


def _register_font() -> str:
    for name, path in MONO_FONTS:
        try:
            pdfmetrics.registerFont(TTFont(name, path))
            return name
        except Exception:
            continue
    return "Courier"


def write_pdf_report(path: Path, result: ScanResult, findings: Iterable[RuleFinding], metadata: dict) -> Path:
    """Generate a PDF summary for the scan results."""

    path.parent.mkdir(parents=True, exist_ok=True)
    font_name = _register_font()
    doc = SimpleDocTemplate(str(path), pagesize=letter, title="DAT Audit Report")
    story: list = []
    heading = ParagraphStyle(name="Heading", fontName=font_name, fontSize=16, textColor=colors.darkgreen)
    body = ParagraphStyle(name="Body", fontName=font_name, fontSize=10, leading=12)

    story.append(Paragraph("DAT Audit Report", heading))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Version: {metadata.get('dat_version')}", body))
    story.append(Paragraph(f"Generated: {metadata.get('generated_at')}", body))
    if lrc := metadata.get("lrc"):
        story.append(Paragraph(f"LRC Project: {lrc.get('project', 'unknown')}", body))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Summary", heading))
    stats = result.stats
    story.append(
        Paragraph(
            f"Scanned {stats.scanned} files with {stats.binary} binary files and {stats.errors} errors.",
            body,
        )
    )
    story.append(Spacer(1, 12))

    if result.skipped:
        story.append(Paragraph("Skipped Files", heading))
        for item in result.skipped[:20]:
            story.append(Paragraph(item, body))
        if len(result.skipped) > 20:
            story.append(Paragraph(f"... {len(result.skipped) - 20} more", body))
        story.append(Spacer(1, 12))

    if findings:
        story.append(Paragraph("Findings", heading))
        for finding in findings:
            location = f" ({finding.path})" if finding.path else ""
            story.append(
                Paragraph(
                    f"[{finding.severity.upper()}] {finding.rule_id}{location}: {finding.message}",
                    body,
                )
            )

    doc.build(story)
    return path
