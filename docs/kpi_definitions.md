# KPI Definitions

Business metrics used in this project and how they are calculated.

---

## Revenue and sales

| KPI | Definition | Calculation |
|-----|------------|-------------|
| **Total Revenue (GMV)** | Total value of payments received for orders in scope | Sum of `payment_value` (payments table) per order, then sum across orders; or directly sum of `fact_orders[revenue]`. |
| **Total Orders** | Number of distinct orders | Count distinct `order_id` in orders / fact_orders. |
| **Average Order Value (AOV)** | Mean revenue per order | Total Revenue ÷ Total Orders. |
| **Revenue by category** | Revenue attributed to each product category | Sum of `price` (order_items) by `product_category_name` (via products), or via fact_order_items and dim_products in Power BI. |
| **Revenue by month** | Total revenue in each calendar month | Group by `year_month` or month from dim_date; sum revenue. |

---

## Customer

| KPI | Definition | Calculation |
|-----|------------|-------------|
| **Unique customers** | Number of distinct customers who placed at least one order | Count distinct `customer_id` in orders. |
| **Orders by state** | Number of orders per customer state | Group orders by `customer_state` (via dim_customers). |
| **Repeat vs one-time** | Share of customers with more than one order | Count customers with `COUNT(order_id) > 1` (repeat) vs `= 1` (one-time). |

---

## Operations and delivery

| KPI | Definition | Calculation |
|-----|------------|-------------|
| **Delivery time (days)** | Days from order purchase to delivery | `(order_delivered_customer_date − order_purchase_timestamp)` in days; stored as `delivery_days` in fact_orders. |
| **Delay (days)** | How many days after estimated delivery the order was delivered | `(order_delivered_customer_date − order_estimated_delivery_date)` in days; stored as `delay_days` (positive = late). |
| **On-time delivery rate** | Percentage of delivered orders delivered on or before estimated date | Count of orders where `order_delivered_customer_date ≤ order_estimated_delivery_date` ÷ total delivered orders; or 100% − (share where `is_late = 1`). |
| **Late orders %** | Percentage of delivered orders delivered after estimated date | Share of orders with `is_late = 1` among orders with non-null delivery date. |
| **Average delivery days** | Mean time from purchase to delivery (in days) | Average of `delivery_days` (fact_orders) for delivered orders. |
| **Average delay by state** | Mean delay (days) per customer state | Average of `delay_days` by `customer_state` (via dim_customers). |

---

## Satisfaction

| KPI | Definition | Calculation |
|-----|------------|-------------|
| **Average review score** | Mean rating (1–5) across reviews | Average of `review_score` (fact_reviews or reviews table). |
| **Review score distribution** | Count of reviews per score (1–5) | Count of reviews grouped by `review_score`. |
| **% low reviews (1–2 stars)** | Share of reviews with score 1 or 2 | Count of reviews where `review_score ≤ 2` ÷ total reviews. |
| **Average score by category** | Mean review score per product category | Average of `review_score` by product category (via order → order_items → products). |
| **Score vs delivery status** | Mean review score for on-time vs late orders | Average of `review_score` grouped by on-time vs late (e.g. using `is_late` or `delay_days`). |

---

## Usage in Power BI

- **Total Revenue:** `SUM(fact_orders[revenue])`
- **Total Orders:** `DISTINCTCOUNT(fact_orders[order_id])`
- **AOV:** `[Total Revenue] / [Total Orders]`
- **On-time %:** e.g. `1 - (SUM(fact_orders[is_late]) / COUNTROWS(fact_orders))` (adjust for filters and nulls as needed)
- **Avg Delivery Days:** `AVERAGE(fact_orders[delivery_days])`
- **Avg Review Score:** `AVERAGE(fact_reviews[review_score])`

Filter to delivered orders where relevant (e.g. for delivery KPIs).
