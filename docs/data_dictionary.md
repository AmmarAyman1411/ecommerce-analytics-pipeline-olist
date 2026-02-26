# Data Dictionary

Reference for the main tables and columns used in this project. Column names reflect the cleaned / Power BI mart naming (snake_case).

---

## Processed tables (data/processed/)

Outputs of the cleaning notebook.

### orders_clean

- **order_id** (Text) — Unique order identifier (PK)
- **customer_id** (Text) — References customers (FK)
- **order_status** (Text) — e.g. delivered, shipped, canceled
- **order_purchase_timestamp** (DateTime) — When the order was placed
- **order_approved_at**, **order_delivered_carrier_date**, **order_delivered_customer_date**, **order_estimated_delivery_date** (DateTime) — Lifecycle dates

### order_items_clean

- **order_id**, **order_item_id**, **product_id**, **seller_id** — Keys and FKs
- **shipping_limit_date** (DateTime) — Seller shipping deadline
- **price**, **freight_value** (Decimal) — Amounts
- **quantity** (Integer) — If present

### customers_clean

- **customer_id** (Text) — PK
- **customer_unique_id**, **customer_zip_code_prefix**, **customer_city**, **customer_state** (Text)

### products_clean

- **product_id** (Text) — PK
- **product_category_name** (Text) — Category
- **product_name_lenght**, **product_description_lenght**, **product_photos_qty**, **product_weight_g**, **product_length_cm**, **product_height_cm**, **product_width_cm** (Numeric)

### sellers_clean

- **seller_id** (Text) — PK
- **seller_zip_code_prefix**, **seller_city**, **seller_state** (Text)

### payments_clean

- **order_id** (Text) — FK
- **payment_sequential**, **payment_installments** (Integer)
- **payment_type** (Text) — e.g. credit_card, boleto
- **payment_value** (Decimal) — Amount paid

### reviews_clean

- **review_id** (Text) — PK
- **order_id** (Text) — FK
- **review_score** (Integer) — 1–5
- **review_comment_title**, **review_comment_message** (Text)
- **review_creation_date**, **review_answer_timestamp** (DateTime)

---

## Power BI mart tables (data/powerbi/)

Built by `src/build_powerbi_mart.py`.

### fact_orders (one row per order)

- **order_id**, **customer_id**, **order_status**
- **order_purchase_timestamp**, **order_delivered_customer_date**, **order_estimated_delivery_date**
- **revenue** (Decimal) — Sum of payment_value for the order
- **item_count**, **items_gmv**, **freight_total**
- **delivery_days** (Decimal) — Days from purchase to delivery
- **delay_days** (Decimal) — Days late (positive = late)
- **is_late** (Integer) — 1 if late, 0 otherwise (when delivered)

### fact_order_items (one row per order line)

- **order_id**, **order_item_id**, **product_id**, **seller_id**
- **shipping_limit_date**, **price**, **freight_value**

### fact_reviews (one row per review)

- **review_id**, **order_id**, **review_score**
- **review_creation_date**, **review_answer_timestamp**
- **delivery_days**, **delay_days**, **is_late** (joined from fact_orders)

### dim_customers, dim_products, dim_sellers

Same structure as the processed customer/product/seller tables; used as dimension lookups.

### dim_date

- **date** (Date) — PK; one row per day in order range
- **year**, **quarter**, **month**, **month_name**, **year_month**, **week**, **weekday**, **weekday_name**, **is_weekend**
