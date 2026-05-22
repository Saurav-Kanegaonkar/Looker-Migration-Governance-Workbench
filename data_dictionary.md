# Data Dictionary

## `data/workbooks.csv`

- `workbook_id`: Synthetic Tableau workbook identifier.
- `workbook_name`: Domain and reporting use case.
- `domain`: Analytics domain such as Commerce, CRM and Loyalty, Retail Media, Digital Shelf, Client Performance, Finance Operations, or Audience Strategy.
- `business_owner`: Owning analytics or BI team.
- `audience`: Primary stakeholder group.
- `criticality`: Tier 1, Tier 2, or Tier 3 migration importance.
- `migration_lane`: Initial migration wave assignment.
- `monthly_views`: Modeled Tableau monthly usage.
- `stakeholder_count`: Stakeholders affected by migration.
- `dashboard_tabs`: Number of Tableau tabs to rationalize.
- `tableau_calc_fields`: Count of Tableau calculated fields to translate.
- `data_sources`: Source count used by the workbook.
- `custom_sql_blocks`: Workbook-level SQL blocks that may need warehouse or LookML redesign.
- `extract_age_hours`: Current Tableau extract freshness lag.
- `uncertified_metrics`: KPI definitions without certification.
- `row_level_security`: Security pattern that must be preserved.
- `tableau_baseline_load_seconds`: Baseline load-time estimate.

## `data/metrics.csv`

- `metric_id`: Synthetic KPI identifier.
- `workbook_id`: Parent Tableau workbook.
- `metric_name`: Business metric.
- `metric_type`: LookML field type.
- `tableau_formula`: Tableau-style formula.
- `lookml_sql`: Target LookML SQL expression.
- `logic_complexity`: Low, medium, or high.
- `definition_owner`: Owner expected to certify the KPI.
- `parity_status`: Pass, tolerance review, or fail.
- `certification_status`: Certified, owner review, or draft.

## `data/lookml_assets.csv`

- `model_name`: Looker model.
- `explore_name`: Target Explore.
- `primary_view`: Base view.
- `join_count`: Number of joined views.
- `join_pattern`: Join relationship pattern.
- `pdt_strategy`: None, PDT, incremental PDT, or aggregate awareness.
- `datagroup`: Cache and PDT refresh policy.
- `cache_policy`: Looker cache configuration.
- `required_filter`: Required filter or `none`.
- `liquid_parameter`: Liquid parameter or `none`.
- `git_review_status`: Approved, needs review, open comments, or blocked.
- `open_review_comments`: Code review comments.
- `style_guide_findings`: LookML style findings.

## `analysis/outputs/*.csv`

Generated outputs rank migration priority, semantic-model risk, and validation or rollout readiness. These files are produced by `scripts/score_operating_data.py`.
