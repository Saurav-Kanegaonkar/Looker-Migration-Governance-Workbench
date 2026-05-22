import csv
import random
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"

random.seed(42)

DOMAINS = [
    ("Commerce", 1.12),
    ("CRM and Loyalty", 1.08),
    ("Retail Media", 1.10),
    ("Digital Shelf", 1.00),
    ("Client Performance", 1.18),
    ("Finance Operations", 0.94),
    ("Audience Strategy", 1.03),
]

WORKBOOK_TYPES = [
    "Executive scorecard",
    "Campaign pacing",
    "Commerce conversion",
    "CRM lifecycle",
    "Retail media performance",
    "Digital shelf availability",
    "Client QBR packet",
    "Finance reconciliation",
]

METRIC_PATTERNS = [
    ("Revenue", "sum(${order_revenue})", "sum(order_revenue)"),
    ("ROAS", "sum(${media_revenue}) / nullif(sum(${media_spend}),0)", "SUM([Media Revenue]) / SUM([Media Spend])"),
    ("Conversion Rate", "sum(${orders}) / nullif(sum(${sessions}),0)", "SUM([Orders]) / SUM([Sessions])"),
    ("Repeat Purchase Rate", "sum(${repeat_customers}) / nullif(sum(${customers}),0)", "SUM([Repeat Customers]) / SUM([Customers])"),
    ("Digital Shelf Availability", "avg(${in_stock_rate})", "AVG([In Stock Rate])"),
    ("Email Revenue Per Send", "sum(${email_revenue}) / nullif(sum(${sends}),0)", "SUM([Email Revenue]) / SUM([Sends])"),
    ("Margin Rate", "sum(${gross_margin}) / nullif(sum(${net_sales}),0)", "SUM([Gross Margin]) / SUM([Net Sales])"),
    ("Qualified Visit Rate", "sum(${qualified_visits}) / nullif(sum(${visits}),0)", "SUM([Qualified Visits]) / SUM([Visits])"),
]


def clamp(value, low, high):
    return max(low, min(high, value))


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build():
    DATA.mkdir(exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    workbooks = []
    metrics = []
    lookml_assets = []
    validation_tests = []
    performance_samples = []
    stakeholder_rollout = []
    roadmap_backlog = []

    owners = ["BI Platform", "Commerce Analytics", "CRM Analytics", "Media Analytics", "Client Reporting"]
    audiences = ["Executive", "Client partner", "Activation team", "Analyst", "Finance"]
    migration_lanes = ["Wave 1", "Wave 2", "Wave 3", "Hold for redesign"]

    start = date(2026, 1, 5)

    for i in range(1, 37):
        domain, multiplier = random.choice(DOMAINS)
        workbook_type = random.choice(WORKBOOK_TYPES)
        criticality = random.choices(["Tier 1", "Tier 2", "Tier 3"], weights=[0.28, 0.45, 0.27])[0]
        calc_fields = random.randint(8, 46)
        data_sources = random.randint(2, 9)
        dashboard_tabs = random.randint(3, 18)
        monthly_views = int(random.triangular(180, 8600, 1850) * multiplier)
        stakeholder_count = random.randint(4, 34) + (12 if criticality == "Tier 1" else 0)
        extract_age_hours = random.randint(2, 72) + (18 if data_sources > 6 else 0)
        uncertified_metrics = random.randint(0, 9) + (3 if calc_fields > 28 else 0)
        custom_sql_blocks = random.randint(0, 7)
        row_level_security = random.choice(["None", "Client filter", "Region filter", "User attribute"])
        baseline_load = round(clamp(random.gauss(8.5, 3.8) + dashboard_tabs * 0.25 + custom_sql_blocks * 0.8, 3.0, 28.0), 1)
        business_owner = random.choice(owners)
        lane = random.choices(migration_lanes, weights=[0.28, 0.34, 0.25, 0.13])[0]
        workbook_id = f"WB{i:03d}"

        workbooks.append(
            {
                "workbook_id": workbook_id,
                "workbook_name": f"{domain} {workbook_type}",
                "domain": domain,
                "business_owner": business_owner,
                "audience": random.choice(audiences),
                "criticality": criticality,
                "migration_lane": lane,
                "monthly_views": monthly_views,
                "stakeholder_count": stakeholder_count,
                "dashboard_tabs": dashboard_tabs,
                "tableau_calc_fields": calc_fields,
                "data_sources": data_sources,
                "custom_sql_blocks": custom_sql_blocks,
                "extract_age_hours": extract_age_hours,
                "uncertified_metrics": uncertified_metrics,
                "row_level_security": row_level_security,
                "tableau_baseline_load_seconds": baseline_load,
            }
        )

        metric_count = random.randint(4, 8)
        sampled_metrics = random.sample(METRIC_PATTERNS, metric_count)
        for idx, (metric_name, lookml_sql, tableau_formula) in enumerate(sampled_metrics, 1):
            metric_id = f"MET{i:03d}_{idx:02d}"
            complexity = random.choices(["Low", "Medium", "High"], weights=[0.24, 0.49, 0.27])[0]
            parity_status = random.choices(["Pass", "Tolerance review", "Fail"], weights=[0.58, 0.27, 0.15])[0]
            metrics.append(
                {
                    "metric_id": metric_id,
                    "workbook_id": workbook_id,
                    "metric_name": metric_name,
                    "metric_type": random.choice(["measure", "dimension_group", "filtered_measure", "parameterized_measure"]),
                    "tableau_formula": tableau_formula,
                    "lookml_sql": lookml_sql,
                    "logic_complexity": complexity,
                    "definition_owner": business_owner,
                    "parity_status": parity_status,
                    "certification_status": random.choices(["Certified", "Owner review", "Draft"], weights=[0.42, 0.38, 0.20])[0],
                }
            )

        explore_name = domain.lower().replace(" and ", "_").replace(" ", "_")
        pdt_strategy = random.choices(["None", "PDT", "Incremental PDT", "Aggregate awareness"], weights=[0.26, 0.31, 0.21, 0.22])[0]
        datagroup = random.choice(["commerce_hourly", "crm_daily", "media_intraday", "finance_daily", "client_weekly"])
        cache_policy = random.choice(["persist_with datagroup", "max_cache_age 4 hours", "max_cache_age 24 hours"])
        git_status = random.choices(["Approved", "Needs review", "Open comments", "Blocked"], weights=[0.36, 0.35, 0.20, 0.09])[0]
        lookml_assets.append(
            {
                "workbook_id": workbook_id,
                "model_name": "agency_analytics",
                "explore_name": explore_name,
                "primary_view": f"{explore_name}_fact",
                "join_count": random.randint(2, 11),
                "join_pattern": random.choice(["many_to_one", "one_to_many review", "fanout risk review"]),
                "pdt_strategy": pdt_strategy,
                "datagroup": datagroup,
                "cache_policy": cache_policy,
                "required_filter": random.choice(["client_id", "reporting_month", "brand_market", "none"]),
                "liquid_parameter": random.choice(["currency_selector", "market_rollup", "channel_grouping", "none"]),
                "git_review_status": git_status,
                "open_review_comments": random.randint(0, 8) + (3 if git_status in {"Open comments", "Blocked"} else 0),
                "style_guide_findings": random.randint(0, 6),
            }
        )

        for test_idx in range(1, 7):
            test_type = random.choice(["Metric parity", "Row count", "Filter behavior", "RLS evidence", "Freshness", "SQL explain"])
            threshold = random.choice([0.5, 1.0, 2.0, 5.0])
            variance = round(abs(random.gauss(0.7, 1.4)) + (1.8 if test_type == "Metric parity" and uncertified_metrics > 5 else 0), 2)
            status = "Pass" if variance <= threshold else ("Tolerance review" if variance <= threshold * 1.7 else "Fail")
            validation_tests.append(
                {
                    "test_id": f"VAL{i:03d}_{test_idx:02d}",
                    "workbook_id": workbook_id,
                    "test_type": test_type,
                    "comparison_source": random.choice(["Tableau extract", "Warehouse SQL", "Certified CSV", "Legacy workbook"]),
                    "threshold_pct": threshold,
                    "observed_variance_pct": variance,
                    "status": status,
                    "owner": business_owner,
                    "evidence_link": f"evidence/{workbook_id.lower()}_{test_idx:02d}.md",
                }
            )

        for sample_idx in range(1, 9):
            sample_date = start + timedelta(days=sample_idx * 7)
            looker_load = round(clamp(baseline_load * random.uniform(0.42, 0.92) + random.uniform(-0.4, 0.8), 1.8, 18.0), 1)
            query_cost = round(random.uniform(0.18, 6.4) * (1.4 if pdt_strategy == "None" else 0.75), 2)
            performance_samples.append(
                {
                    "sample_date": sample_date.isoformat(),
                    "workbook_id": workbook_id,
                    "tableau_load_seconds": baseline_load,
                    "looker_load_seconds": looker_load,
                    "warehouse_query_cost": query_cost,
                    "cache_hit_rate_pct": round(clamp(random.gauss(68, 15) + (10 if cache_policy == "persist_with datagroup" else 0), 18, 96), 1),
                    "pdt_build_minutes": round(0 if pdt_strategy == "None" else random.uniform(4, 38), 1),
                }
            )

        stakeholder_rollout.append(
            {
                "workbook_id": workbook_id,
                "training_status": random.choices(["Complete", "Scheduled", "Not started"], weights=[0.38, 0.43, 0.19])[0],
                "adoption_status": random.choices(["Ready", "Pilot", "At risk"], weights=[0.42, 0.40, 0.18])[0],
                "open_incidents": random.randint(0, 7) + (2 if criticality == "Tier 1" else 0),
                "stakeholder_sentiment": random.choices(["Positive", "Mixed", "Concerned"], weights=[0.46, 0.39, 0.15])[0],
                "cutover_readiness": random.choices(["Ready", "Needs owner signoff", "Blocked"], weights=[0.42, 0.43, 0.15])[0],
                "last_enablement_date": (start + timedelta(days=random.randint(12, 128))).isoformat(),
            }
        )

        roadmap_backlog.append(
            {
                "initiative_id": f"RM{i:03d}",
                "workbook_id": workbook_id,
                "epic": random.choice(["Metric certification", "Explore redesign", "Performance tuning", "Training and adoption", "Security review"]),
                "user_story": f"As a {random.choice(audiences).lower()} user, I need trusted {domain.lower()} metrics in Looker.",
                "business_impact": random.choice(["High", "Medium", "Low"]),
                "effort_points": random.choice([3, 5, 8, 13]),
                "release_target": random.choice(["Sprint 1", "Sprint 2", "Sprint 3", "Migration wave backlog"]),
                "status": random.choice(["Ready", "In discovery", "Blocked", "In review"]),
            }
        )

    write_csv(
        DATA / "workbooks.csv",
        workbooks,
        [
            "workbook_id",
            "workbook_name",
            "domain",
            "business_owner",
            "audience",
            "criticality",
            "migration_lane",
            "monthly_views",
            "stakeholder_count",
            "dashboard_tabs",
            "tableau_calc_fields",
            "data_sources",
            "custom_sql_blocks",
            "extract_age_hours",
            "uncertified_metrics",
            "row_level_security",
            "tableau_baseline_load_seconds",
        ],
    )
    write_csv(
        DATA / "metrics.csv",
        metrics,
        [
            "metric_id",
            "workbook_id",
            "metric_name",
            "metric_type",
            "tableau_formula",
            "lookml_sql",
            "logic_complexity",
            "definition_owner",
            "parity_status",
            "certification_status",
        ],
    )
    write_csv(
        DATA / "lookml_assets.csv",
        lookml_assets,
        [
            "workbook_id",
            "model_name",
            "explore_name",
            "primary_view",
            "join_count",
            "join_pattern",
            "pdt_strategy",
            "datagroup",
            "cache_policy",
            "required_filter",
            "liquid_parameter",
            "git_review_status",
            "open_review_comments",
            "style_guide_findings",
        ],
    )
    write_csv(
        DATA / "validation_tests.csv",
        validation_tests,
        [
            "test_id",
            "workbook_id",
            "test_type",
            "comparison_source",
            "threshold_pct",
            "observed_variance_pct",
            "status",
            "owner",
            "evidence_link",
        ],
    )
    write_csv(
        DATA / "performance_samples.csv",
        performance_samples,
        [
            "sample_date",
            "workbook_id",
            "tableau_load_seconds",
            "looker_load_seconds",
            "warehouse_query_cost",
            "cache_hit_rate_pct",
            "pdt_build_minutes",
        ],
    )
    write_csv(
        DATA / "stakeholder_rollout.csv",
        stakeholder_rollout,
        [
            "workbook_id",
            "training_status",
            "adoption_status",
            "open_incidents",
            "stakeholder_sentiment",
            "cutover_readiness",
            "last_enablement_date",
        ],
    )
    write_csv(
        DATA / "roadmap_backlog.csv",
        roadmap_backlog,
        [
            "initiative_id",
            "workbook_id",
            "epic",
            "user_story",
            "business_impact",
            "effort_points",
            "release_target",
            "status",
        ],
    )


if __name__ == "__main__":
    build()
