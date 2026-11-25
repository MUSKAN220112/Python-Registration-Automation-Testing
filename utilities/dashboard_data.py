import json
import logging
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path


LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"


class _PytestReportParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data_blob = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get("id") == "data-container":
            self.data_blob = attributes.get("data-jsonblob")


def _read_project_description():
    readme = PROJECT_ROOT / "README.md"
    try:
        lines = readme.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        LOGGER.warning("Unable to read project README %s: %s", readme, error)
        return PROJECT_ROOT.name.replace("_", " "), ""

    title = next((line.lstrip("# ").strip() for line in lines if line.startswith("# ")), None)
    description = next(
        (line.strip() for line in lines if line.strip() and not line.startswith("#")),
        "",
    )
    return title or PROJECT_ROOT.name.replace("_", " "), description


def _read_pytest_report():
    report_path = REPORTS_DIR / "pytest-report.html"
    if not report_path.is_file():
        return None, []

    try:
        parser = _PytestReportParser()
        parser.feed(report_path.read_text(encoding="utf-8"))
        report_data = json.loads(parser.data_blob) if parser.data_blob else {}
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        LOGGER.warning("Unable to read pytest report %s: %s", report_path, error)
        return None, []

    test_data = report_data.get("tests")
    if not isinstance(test_data, dict):
        LOGGER.warning("Pytest report %s has no test results", report_path)
        return None, []

    test_cases = []
    for node_id, entries in test_data.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            test_cases.append({
                "name": entry.get("testId") or node_id,
                "status": str(entry.get("result") or "Unknown").title(),
                "duration": entry.get("duration") or "",
            })

    statuses = [case["status"].casefold() for case in test_cases]
    updated_at = datetime.fromtimestamp(report_path.stat().st_mtime).astimezone()
    summary = {
        "total": len(test_cases),
        "passed": sum(status == "passed" for status in statuses),
        "failed": sum(status in {"failed", "error", "broken"} for status in statuses),
        "skipped": sum(status in {"skipped", "xfailed"} for status in statuses),
        "updated_at": updated_at.strftime("%b %d, %Y at %I:%M %p"),
    }
    return summary, test_cases


def _read_executions():
    results_dir = REPORTS_DIR / "allure-results"
    if not results_dir.is_dir():
        return []

    executions = []
    for result_path in results_dir.glob("*-result.json"):
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            LOGGER.warning("Unable to read Allure result %s: %s", result_path, error)
            continue

        started = result.get("start")
        if not isinstance(started, (int, float)):
            continue
        stopped = result.get("stop")
        duration = max(0, int(stopped - started)) if isinstance(stopped, (int, float)) else None
        executions.append({
            "name": result.get("name") or result_path.stem,
            "status": str(result.get("status") or "Unknown").title(),
            "started_at": datetime.fromtimestamp(started / 1000).astimezone().strftime(
                "%b %d, %Y at %I:%M %p"
            ),
            "duration": f"{duration} ms" if duration is not None else "—",
            "sort_key": started,
        })

    executions.sort(key=lambda item: item["sort_key"], reverse=True)
    for execution in executions:
        execution.pop("sort_key")
    return executions


def get_dashboard_data():
    project_name, description = _read_project_description()
    summary, test_cases = _read_pytest_report()
    reports = []
    if REPORTS_DIR.is_dir():
        for report_path in sorted(REPORTS_DIR.glob("*.html")):
            reports.append({
                "filename": report_path.name,
                "name": report_path.stem.replace("-", " ").replace("_", " ").title(),
                "updated_at": datetime.fromtimestamp(report_path.stat().st_mtime).astimezone().strftime(
                    "%b %d, %Y at %I:%M %p"
                ),
            })

    if summary and summary["total"]:
        project_status = "Failed" if summary["failed"] else "Passed"
    else:
        project_status = "No report"

    projects = [{
        "name": project_name,
        "description": description,
        "status": project_status,
    }]
    executions = _read_executions()
    return {
        "projects": projects,
        "summary": summary,
        "test_cases": test_cases,
        "reports": reports,
        "recent_executions": executions[:8],
        "total_executions": len(executions),
    }
