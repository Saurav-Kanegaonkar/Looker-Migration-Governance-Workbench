view: campaigns {
  sql_table_name: analytics.campaigns ;;

  dimension: campaign_id {
    primary_key: yes
    type: string
    sql: ${TABLE}.campaign_id ;;
  }

  dimension: channel_group {
    type: string
    sql:
      {% if channel_rollup._parameter_value == "paid_owned" %}
        ${TABLE}.paid_owned_channel
      {% else %}
        ${TABLE}.standard_channel
      {% endif %} ;;
  }

  parameter: channel_rollup {
    type: string
    allowed_value: {
      label: "Standard"
      value: "standard"
    }
    allowed_value: {
      label: "Paid And Owned"
      value: "paid_owned"
    }
  }
}
