view: commerce_performance {
  derived_table: {
    datagroup_trigger: commerce_hourly
    indexes: ["client_id", "campaign_id", "reporting_date"]
    sql:
      select
        client_id,
        campaign_id,
        reporting_date,
        order_revenue,
        media_revenue,
        media_spend,
        orders,
        sessions,
        gross_margin,
        net_sales
      from analytics.commerce_performance_daily ;;
  }

  dimension: client_id {
    primary_key: yes
    type: string
    sql: ${TABLE}.client_id ;;
  }

  dimension_group: reporting {
    type: time
    timeframes: [date, week, month, quarter, year]
    sql: ${TABLE}.reporting_date ;;
  }

  measure: revenue {
    type: sum
    value_format_name: usd
    sql: ${TABLE}.order_revenue ;;
  }

  measure: roas {
    type: number
    value_format_name: decimal_2
    sql: sum(${TABLE}.media_revenue) / nullif(sum(${TABLE}.media_spend), 0) ;;
  }

  measure: conversion_rate {
    type: number
    value_format_name: percent_2
    sql: sum(${TABLE}.orders) / nullif(sum(${TABLE}.sessions), 0) ;;
  }
}
