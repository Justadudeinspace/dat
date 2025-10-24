"""Policy driven severity rule evaluation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence


@dataclass(frozen=True)
class Rule:
    """A single audit rule."""

    rule_id: str
    description: str
    patterns: Sequence[str]
    severity: str = "medium"


@dataclass(frozen=True)
class RuleViolation:
    """Represents a match against a rule."""

    rule_id: str
    severity: str
    message: str
    path: str
    line_number: int | None = None


@dataclass
class Policy:
    """Container for active audit rules."""

    rules: List[Rule]

    def evaluate(self, *, path: Path, lines: Iterable[str]) -> List[RuleViolation]:
        """Evaluate policy rules against a file stream."""

        violations: List[RuleViolation] = []
        for line_number, line in enumerate(lines, start=1):
            stripped = line.strip()
            for rule in self.rules:
                for pattern in rule.patterns:
                    if pattern in stripped:
                        violations.append(
                            RuleViolation(
                                rule_id=rule.rule_id,
                                severity=rule.severity,
                                message=f"Matched pattern '{pattern}'",
                                path=str(path),
                                line_number=line_number,
                            )
                        )
        return violations


DEFAULT_RULES = [
    Rule(
        rule_id="secrets.api_key",
        description="Potential API key exposure",
        patterns=("API_KEY", "SECRET_KEY", "x-api-key"),
        severity="high",
    ),
    Rule(
        rule_id="credentials.password",
        description="Potential password in source",
        patterns=("password=", "pwd=", "PASS="),
        severity="critical",
    ),
    Rule(
        rule_id="compliance.todo",
        description="TODO found in tracked files",
        patterns=("TODO",),
        severity="low",
    ),
]


def load_default_policy(extra_rules: Sequence[Rule] | None = None) -> Policy:
    """Return the default policy merged with *extra_rules*."""

    rules = list(DEFAULT_RULES)
    if extra_rules:
        rules.extend(extra_rules)
    return Policy(rules=rules)
