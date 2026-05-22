# Data Sources

All datasets in this folder are synthetic and generated for a public portfolio artifact. They do not represent real client, agency, employee, customer, financial, media, CRM, or commerce performance data.

The generated structure models a BI platform team migrating a portfolio of Tableau assets into a governed Looker semantic layer for a multi-brand digital experience and commerce analytics environment.

## Generated Files

- `workbooks.csv`: Tableau workbook inventory, business owner, audience, criticality, usage, complexity, extract age, custom SQL, row-level security, and baseline load time.
- `metrics.csv`: Tableau calculated fields mapped to LookML dimensions, measures, filtered measures, and parameters.
- `lookml_assets.csv`: Looker model, Explore, view, join pattern, PDT strategy, datagroup, cache policy, Liquid parameter, and Git review state.
- `validation_tests.csv`: Metric parity, row count, filter behavior, row-level security, freshness, and SQL explain checks.
- `performance_samples.csv`: Tableau baseline load, Looker target load, query cost, cache hit rate, and PDT build time samples.
- `stakeholder_rollout.csv`: Training, adoption, incident, sentiment, and cutover readiness status.
- `roadmap_backlog.csv`: Product backlog stories, epics, release targets, effort points, and status.

## Synthetic Generation Logic

The generator uses a fixed random seed so the artifact is reproducible.

- Tier 1 workbooks receive higher stakeholder exposure and stricter cutover expectations.
- Workbooks with many calculated fields, data sources, custom SQL blocks, and dashboard tabs receive higher migration complexity.
- Metric parity failures are more common where the Tableau asset has many uncertified metrics.
- PDT, incremental PDT, and aggregate-awareness strategies are assigned to assets with heavier semantic-model and performance needs.
- Datagroups model common refresh patterns such as hourly commerce, daily CRM, intraday media, daily finance, and weekly client reporting.
- Looker load times are modeled as an improvement over Tableau baseline load times, with cache policy and PDT strategy affecting expected performance.
- Rollout risk increases when training is incomplete, adoption is at risk, incidents are open, or cutover readiness is blocked.
