# Insights Report

Short summary of analytical findings from the Olist e-commerce analytics project.

---

## Revenue and sales

- **Trend:** Monthly revenue and order volume show a clear trend over the analysis period; growth and seasonality can be identified from the time series.
- **Top categories:** A small set of product categories (e.g. bed_bath_table, health_beauty, sports_leisure) typically drive the largest share of revenue; the exact top 5–10 can be read from the EDA notebook and Power BI dashboard.
- **Geography:** A few states (notably SP) concentrate most orders and revenue; the dashboard supports drill-down by state and category.

---

## Delivery performance

- **Average delivery time:** Delivery days from purchase to customer delivery vary by region and category; the overall average is reported in the Operations page of the dashboard.
- **On-time rate:** A large proportion of orders are delivered on or before the estimated date; the remainder are late and captured by the “Late orders %” and “Avg delay by state” metrics.
- **Delay hotspots:** Some states show higher average delay (days late), which helps prioritize logistics and carrier improvements.

---

## Customer satisfaction

- **Review scores:** Average review score sits in the mid range (e.g. 4.x out of 5); distribution across 1–5 stars is available in the dashboard.
- **Low reviews:** The share of 1–2 star reviews is a useful proxy for dissatisfaction; it can be broken down by category, state, or delivery performance.
- **Delivery and satisfaction:** Late deliveries tend to be associated with lower average review scores; the “score vs delivery status” visual on the Customer & Satisfaction page illustrates this.

---

## Recommendations (illustrative)

- **Operations:** Focus on states with the highest average delay and investigate causes (carrier, distance, product type).
- **Catalog:** Double down on top revenue categories and review underperformers for assortment or pricing.
- **Satisfaction:** Use “score vs delivery status” and “score by category” to target improvements in logistics and product quality.

---

*For exact numbers and visuals, refer to the Jupyter EDA notebooks and the Power BI dashboard (Executive Overview, Operations, Customer & Satisfaction pages).*
