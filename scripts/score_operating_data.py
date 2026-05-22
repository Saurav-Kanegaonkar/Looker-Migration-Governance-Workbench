import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"


def read_csv(name):
    with (DATA / name).open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def numeric(value):
    return float(value)


def avg(values):
    return sum(values) / len(values) if values else 0.0


def criticality_weight(value):
    return {"Tier 1": 24, "Tier 2": 14, "Tier 3": 7}.get(value, 0)


def status_count(rows, field, status):
    return sum(1 for row in rows if row[field] == status)


def main():
    workbooks = read_csv("workbooks.csv")
    metrics = read_csv("metrics.csv")
    lookml_assets = read_csv("lookml_assets.csv")
    validation_tests = read_csv("validation_tests.csv")
    performance_samples = read_csv("performance_samples.csv")
    rollout = read_csv("stakeholder_rollout.csv")
    roadmap = read_csv("roadmap_backlog.csv")

    metrics_by_workbook = defaultdict(list)
    tests_by_workbook = defaultdict(list)
    perf_by_workbook = defaultdict(list)
    roadmap_by_workbook = defaultdict(list)
    lookml_by_workbook = {}
    rollout_by_workbook = {}

    for row in metrics:
        metrics_by_workbook[row["workbook_id"]].append(row)
    for row in validation_tests:
        tests_by_workbook[row["workbook_id"]].append(row)
    for row in performance_samples:
        perf_by_workbook[row["workbook_id"]].append(row)
    for row in roadmap:
        roadmap_by_workbook[row["workbook_id"]].append(row)
    for row in lookml_assets:
        lookml_by_workbook[row["workbook_id"]] = row
    for row in rollout:
        rollout_by_workbook[row["workbook_id"]] = row

    migration_rows = []
    governance_rows = []
    validation_rows = []

    for workbook in workbooks:
        workbook_id = workbook["workbook_id"]
        workbook_metrics = metrics_by_workbook[workbook_id]
        workbook_tests = tests_by_workbook[workbook_id]
        workbook_perf = perf_by_workbook[workbook_id]
        lookml = lookml_by_workbook[workbook_id]
        rollout_row = rollout_by_workbook[workbook_id]
        roadmap_rows = roadmap_by_workbook[workbook_id]

        failed_tests = status_count(workbook_tests, "status", "Fail")
        review_tests = status_count(workbook_tests, "status", "Tolerance review")
        parity_pass_rate = round(100 * status_count(workbook_tests, "status", "Pass") / len(workbook_tests), 1)
        certified_rate = round(100 * status_count(workbook_metrics, "certification_status", "Certified") / len(workbook_metrics), 1)
        metric_review_count = sum(1 for row in workbook_metrics if row["parity_status"] != "Pass")
        avg_tableau_load = avg([numeric(row["tableau_load_seconds"]) for row in workbook_perf])
        avg_looker_load = avg([numeric(row["looker_load_seconds"]) for row in workbook_perf])
        avg_cache_hit = avg([numeric(row["cache_hit_rate_pct"]) for row in workbook_perf])
        load_improvement = round(100 * (avg_tableau_load - avg_looker_load) / avg_tableau_load, 1)

        complexity_score = (
            numeric(workbook["tableau_calc_fields"]) * 0.8
            + numeric(workbook["data_sources"]) * 3
            + numeric(workbook["custom_sql_blocks"]) * 4
            + numeric(workbook["dashboard_tabs"]) * 0.9
        )
        usage_score = min(numeric(workbook["monthly_views"]) / 120, 50) + min(numeric(workbook["stakeholder_count"]) * 1.4, 38)
        validation_risk = failed_tests * 14 + review_tests * 6 + metric_review_count * 3
        governance_risk = (
            numeric(workbook["uncertified_metrics"]) * 4
            + numeric(lookml["open_review_comments"]) * 5
            + numeric(lookml["style_guide_findings"]) * 3
        )
        readiness_penalty = 0
        readiness_penalty += 18 if rollout_row["cutover_readiness"] == "Blocked" else 0
        readiness_penalty += 10 if rollout_row["training_status"] == "Not started" else 0
        readiness_penalty += 9 if rollout_row["adoption_status"] == "At risk" else 0
        priority_score = round(
            criticality_weight(workbook["criticality"]) + usage_score + complexity_score * 0.42 + validation_risk + readiness_penalty,
            1,
        )
        readiness_score = round(max(0, 100 - validation_risk - governance_risk * 0.55 - readiness_penalty), 1)

        if readiness_score >= 78 and failed_tests == 0 and rollout_row["cutover_readiness"] == "Ready":
            lane = "Ready for Looker cutover"
        elif failed_tests > 1 or rollout_row["cutover_readiness"] == "Blocked":
            lane = "Blocker remediation"
        else:
            lane = "Owner validation"

        migration_rows.append(
            {
                "workbook_id": workbook_id,
                "workbook_name": workbook["workbook_name"],
                "domain": workbook["domain"],
                "criticality": workbook["criticality"],
                "migration_lane": workbook["migration_lane"],
                "priority_score": priority_score,
                "readiness_score": readiness_score,
                "monthly_views": workbook["monthly_views"],
                "metric_count": len(workbook_metrics),
                "parity_pass_rate": parity_pass_rate,
                "certified_metric_rate": certified_rate,
                "load_improvement_pct": load_improvement,
                "cutover_lane": lane,
                "next_action": next_action(lane, failed_tests, metric_review_count, rollout_row),
            }
        )

        governance_rows.append(
            {
                "workbook_id": workbook_id,
                "explore_name": lookml["explore_name"],
                "primary_view": lookml["primary_view"],
                "join_pattern": lookml["join_pattern"],
                "join_count": lookml["join_count"],
                "pdt_strategy": lookml["pdt_strategy"],
                "datagroup": lookml["datagroup"],
                "cache_policy": lookml["cache_policy"],
                "liquid_parameter": lookml["liquid_parameter"],
                "git_review_status": lookml["git_review_status"],
                "open_review_comments": lookml["open_review_comments"],
                "style_guide_findings": lookml["style_guide_findings"],
                "semantic_risk_score": round(governance_risk + metric_review_count * 5 + (12 if lookml["join_pattern"] != "many_to_one" else 0), 1),
            }
        )

        validation_rows.append(
            {
                "workbook_id": workbook_id,
                "workbook_name": workbook["workbook_name"],
                "failed_tests": failed_tests,
                "tolerance_reviews": review_tests,
                "parity_pass_rate": parity_pass_rate,
                "avg_tableau_load_seconds": round(avg_tableau_load, 1),
                "avg_looker_load_seconds": round(avg_looker_load, 1),
                "load_improvement_pct": load_improvement,
                "avg_cache_hit_rate_pct": round(avg_cache_hit, 1),
                "training_status": rollout_row["training_status"],
                "adoption_status": rollout_row["adoption_status"],
                "open_incidents": rollout_row["open_incidents"],
                "cutover_readiness": rollout_row["cutover_readiness"],
                "roadmap_items": len(roadmap_rows),
            }
        )

    migration_rows.sort(key=lambda row: numeric(row["priority_score"]), reverse=True)
    governance_rows.sort(key=lambda row: numeric(row["semantic_risk_score"]), reverse=True)
    validation_rows.sort(key=lambda row: (int(row["failed_tests"]), int(row["open_incidents"]), -numeric(row["parity_pass_rate"])), reverse=True)

    write_csv(
        OUTPUTS / "migration_priority_queue.csv",
        migration_rows,
        [
            "workbook_id",
            "workbook_name",
            "domain",
            "criticality",
            "migration_lane",
            "priority_score",
            "readiness_score",
            "monthly_views",
            "metric_count",
            "parity_pass_rate",
            "certified_metric_rate",
            "load_improvement_pct",
            "cutover_lane",
            "next_action",
        ],
    )
    write_csv(
        OUTPUTS / "lookml_governance_queue.csv",
        governance_rows,
        [
            "workbook_id",
            "explore_name",
            "primary_view",
            "join_pattern",
            "join_count",
            "pdt_strategy",
            "datagroup",
            "cache_policy",
            "liquid_parameter",
            "git_review_status",
            "open_review_comments",
            "style_guide_findings",
            "semantic_risk_score",
        ],
    )
    write_csv(
        OUTPUTS / "validation_rollout_queue.csv",
        validation_rows,
        [
            "workbook_id",
            "workbook_name",
            "failed_tests",
            "tolerance_reviews",
            "parity_pass_rate",
            "avg_tableau_load_seconds",
            "avg_looker_load_seconds",
            "load_improvement_pct",
            "avg_cache_hit_rate_pct",
            "training_status",
            "adoption_status",
            "open_incidents",
            "cutover_readiness",
            "roadmap_items",
        ],
    )

    summary = {
        "workbooks": len(workbooks),
        "metrics": len(metrics),
        "validation_tests": len(validation_tests),
        "tier_1_workbooks": sum(1 for row in workbooks if row["criticality"] == "Tier 1"),
        "ready_for_cutover": sum(1 for row in migration_rows if row["cutover_lane"] == "Ready for Looker cutover"),
        "blocker_remediation": sum(1 for row in migration_rows if row["cutover_lane"] == "Blocker remediation"),
        "avg_parity_pass_rate": round(avg([numeric(row["parity_pass_rate"]) for row in migration_rows]), 1),
        "avg_load_improvement_pct": round(avg([numeric(row["load_improvement_pct"]) for row in migration_rows]), 1),
        "top_domain": Counter(row["domain"] for row in migration_rows[:10]).most_common(1)[0][0],
        "top_priority_workbook": migration_rows[0],
        "highest_semantic_risk": governance_rows[0],
    }

    with (OUTPUTS / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    print(f"Wrote {len(migration_rows)} migration queue rows")
    print(f"Ready for cutover: {summary['ready_for_cutover']}")
    print(f"Blocker remediation: {summary['blocker_remediation']}")
    print(f"Average parity pass rate: {summary['avg_parity_pass_rate']}%")


def next_action(lane, failed_tests, metric_review_count, rollout_row):
    if lane == "Ready for Looker cutover":
        return "Schedule production cutover and archive Tableau duplicate"
    if failed_tests > 1:
        return "Resolve failed parity tests with metric owner and warehouse SQL evidence"
    if rollout_row["cutover_readiness"] == "Blocked":
        return "Clear cutover blocker before adding this asset to a release wave"
    if metric_review_count > 2:
        return "Complete KPI definition review and LookML certification"
    return "Run owner validation and prepare enablement notes"


if __name__ == "__main__":
    main()
