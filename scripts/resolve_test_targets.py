#!/usr/bin/env python3

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config.suite_map import SUITE_MAP


GROUPS = {
    "safety-smoke": ["safety.settings", "safety.publicApi.*"],
    "safety-core": ["safety.settings", "safety.publicApi.*", "safety.reports.*"],
    "safety-driver-subset": ["safety.settings", "safety.safetyDriverApp.*"],
}


def resolve_suite_pattern(selection: str) -> str:
    if selection in SUITE_MAP:
        return SUITE_MAP[selection]
    if selection.startswith("com.gomotive."):
        return selection
    if "*" in selection:
        return f"com.gomotive.system.tests.{selection}"
    if "." in selection:
        return f"com.gomotive.system.tests.{selection}.*"
    return f"com.gomotive.system.tests.{selection}.*"


def discover_classes_for_pattern(pattern: str, tests_root: Path) -> list[str]:
    if "*" not in pattern:
        return [pattern]

    if not pattern.endswith(".*"):
        raise ValueError(f"Only package-style patterns are supported for class parallelization: {pattern}")

    package_name = pattern[:-2]
    package_path = tests_root / Path(package_name.replace(".", "/"))
    if not package_path.exists():
        raise ValueError(f"Package path not found for pattern {pattern}: {package_path}")

    classes = []
    for java_file in sorted(package_path.rglob("*.java")):
        if not (java_file.name.endswith("Test.java") or java_file.name.endswith("Tests.java")):
            continue
        rel = java_file.relative_to(tests_root)
        fqcn = ".".join(rel.with_suffix("").parts)
        classes.append(fqcn)

    if not classes:
        raise ValueError(f"No test classes discovered for pattern {pattern}")

    return classes


def main() -> int:
    if len(sys.argv) != 7:
        print(
            "Usage: resolve_test_targets.py <run_mode> <suite_group> <pod> <sub_package> <parallel_level> <framework_root>",
            file=sys.stderr,
        )
        return 1

    run_mode, suite_group, pod, sub_package, parallel_level, framework_root = sys.argv[1:]
    tests_root = (
        Path(framework_root)
        / "gomotive-system-tests"
        / "api-system-tests"
        / "src"
        / "test"
        / "java"
    )

    if run_mode == "group":
        if suite_group not in GROUPS:
            raise ValueError(f"Unknown suite group: {suite_group}")
        selected_suites = GROUPS[suite_group]
        selection_label = suite_group
    else:
        selection = sub_package or pod or "safety.settings"
        selected_suites = [selection]
        selection_label = selection

    targets = []
    for suite in selected_suites:
        resolved_pattern = resolve_suite_pattern(suite)
        if parallel_level == "class":
            for fqcn in discover_classes_for_pattern(resolved_pattern, tests_root):
                targets.append(
                    {
                        "target": fqcn,
                        "label": fqcn.rsplit(".", 1)[-1],
                        "source_suite": suite,
                    }
                )
        else:
            targets.append(
                {
                    "target": suite,
                    "label": suite,
                    "source_suite": suite,
                }
            )

    output = {
        "selection_label": selection_label,
        "matrix": {"include": targets},
    }
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
