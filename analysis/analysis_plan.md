# Analysis Plan

## Objective

Rank Tableau assets for safe Looker migration, identify semantic-layer governance risks, and create a release-ready control view for validation, performance, stakeholder enablement, and roadmap sequencing.

## Questions

1. Which Tableau workbooks should move first based on business value, usage, criticality, and migration complexity?
2. Which assets need metric-owner review before their Tableau logic can be certified in LookML?
3. Which Explores carry semantic-model risk because of join pattern, PDT strategy, cache policy, Liquid parameters, or open Git review comments?
4. Which assets are blocked by parity failures, performance gaps, incomplete training, incidents, or cutover readiness?

## Method

1. Generate synthetic workbook, KPI, LookML, validation, performance, rollout, and roadmap data.
2. Join each dataset at `workbook_id` grain.
3. Compute migration priority from business criticality, usage, complexity, validation risk, and readiness penalties.
4. Compute readiness from parity failures, certification status, Git review state, style-guide findings, training status, adoption status, and cutover readiness.
5. Compute semantic risk from LookML review comments, style findings, metric parity review count, and nonstandard join pattern.
6. Assign each workbook to a cutover lane: `Ready for Looker cutover`, `Owner validation`, or `Blocker remediation`.

## Outputs

- `analysis/outputs/migration_priority_queue.csv`
- `analysis/outputs/lookml_governance_queue.csv`
- `analysis/outputs/validation_rollout_queue.csv`
- `analysis/outputs/summary.json`
