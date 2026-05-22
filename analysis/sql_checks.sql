-- Tableau workbook inventory with migration complexity.
select
  workbook_id,
  workbook_name,
  domain,
  criticality,
  monthly_views,
  tableau_calc_fields,
  data_sources,
  custom_sql_blocks,
  extract_age_hours
from workbooks
order by monthly_views desc;

-- KPI parity checks that block semantic-layer certification.
select
  m.workbook_id,
  m.metric_name,
  m.metric_type,
  m.parity_status,
  m.certification_status,
  v.test_type,
  v.observed_variance_pct,
  v.status
from metrics m
join validation_tests v
  on m.workbook_id = v.workbook_id
where m.parity_status <> 'Pass'
   or v.status = 'Fail';

-- LookML review queue for join, PDT, datagroup, cache, and Git governance.
select
  workbook_id,
  explore_name,
  primary_view,
  join_pattern,
  pdt_strategy,
  datagroup,
  cache_policy,
  liquid_parameter,
  git_review_status,
  open_review_comments,
  style_guide_findings
from lookml_assets
where git_review_status <> 'Approved'
   or join_pattern <> 'many_to_one'
   or open_review_comments > 0
order by open_review_comments desc;

-- Cutover readiness controls for launch planning.
select
  r.workbook_id,
  r.training_status,
  r.adoption_status,
  r.open_incidents,
  r.stakeholder_sentiment,
  r.cutover_readiness,
  q.parity_pass_rate,
  q.load_improvement_pct
from stakeholder_rollout r
join migration_priority_queue q
  on r.workbook_id = q.workbook_id
where r.cutover_readiness <> 'Ready'
   or r.open_incidents > 0
   or q.parity_pass_rate < 95;
