connection: "warehouse_connection"

include: "/views/*.view.lkml"

datagroup: commerce_hourly {
  sql_trigger: select max(updated_at) from analytics.commerce_orders ;;
  max_cache_age: "4 hours"
}

datagroup: crm_daily {
  sql_trigger: select max(updated_at) from analytics.crm_customer_daily ;;
  max_cache_age: "24 hours"
}

explore: commerce_performance {
  label: "Commerce Performance"
  persist_with: commerce_hourly

  always_filter: {
    filters: [client_id: "-NULL"]
  }

  join: campaigns {
    type: left_outer
    relationship: many_to_one
    sql_on: ${commerce_performance.campaign_id} = ${campaigns.campaign_id} ;;
  }
}

explore: crm_lifecycle {
  label: "CRM Lifecycle"
  persist_with: crm_daily

  join: customers {
    type: left_outer
    relationship: many_to_one
    sql_on: ${crm_lifecycle.customer_id} = ${customers.customer_id} ;;
  }
}
