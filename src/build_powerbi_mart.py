from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Paths:
    base_dir: Path
    processed_dir: Path
    powerbi_dir: Path


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        pd.Index(df.columns)
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]+", "_", regex=True)  # spaces, hyphens, etc -> _
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )
    return df


def _ensure_numeric(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _parse_dates(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


def _read_processed_csv(paths: Paths, filename: str) -> pd.DataFrame:
    p = paths.processed_dir / filename
    if not p.exists():
        raise FileNotFoundError(f"Missing required file: {p}")
    df = pd.read_csv(p)
    return _normalize_columns(df)


def _build_dim_date(min_dt: pd.Timestamp, max_dt: pd.Timestamp) -> pd.DataFrame:
    start = pd.to_datetime(min_dt).normalize()
    end = pd.to_datetime(max_dt).normalize()
    if pd.isna(start) or pd.isna(end):
        raise ValueError("Cannot build dim_date: purchase timestamp range is missing.")

    dates = pd.date_range(start=start, end=end, freq="D")
    df = pd.DataFrame({"date": dates})
    df["year"] = df["date"].dt.year
    df["quarter"] = df["date"].dt.quarter
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")
    df["year_month"] = df["date"].dt.strftime("%Y-%m")
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["weekday"] = df["date"].dt.weekday + 1  # Monday=1
    df["weekday_name"] = df["date"].dt.strftime("%a")
    df["is_weekend"] = df["weekday"].isin([6, 7]).astype(int)
    return df


def build_powerbi_mart() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    paths = Paths(
        base_dir=base_dir,
        processed_dir=base_dir / "data" / "processed",
        powerbi_dir=base_dir / "data" / "powerbi",
    )
    paths.powerbi_dir.mkdir(parents=True, exist_ok=True)

    # ---- Load cleaned sources (from Phase 1)
    orders = _read_processed_csv(paths, "orders_clean.csv")
    order_items = _read_processed_csv(paths, "order_items_clean.csv")
    customers = _read_processed_csv(paths, "customers_clean.csv")
    products = _read_processed_csv(paths, "products_clean.csv")
    sellers = _read_processed_csv(paths, "sellers_clean.csv")
    payments = _read_processed_csv(paths, "payments_clean.csv")
    reviews = _read_processed_csv(paths, "reviews_clean.csv")

    # ---- Types
    orders = _parse_dates(
        orders,
        [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )

    order_items = _parse_dates(order_items, ["shipping_limit_date"])
    order_items = _ensure_numeric(order_items, ["order_item_id", "price", "freight_value"])

    payments = _ensure_numeric(
        payments,
        ["payment_sequential", "payment_installments", "payment_value"],
    )

    reviews = _parse_dates(reviews, ["review_creation_date", "review_answer_timestamp"])
    reviews = _ensure_numeric(reviews, ["review_score"])

    # ---- Facts
    revenue_by_order = (
        payments.groupby("order_id", as_index=False)["payment_value"].sum().rename(columns={"payment_value": "revenue"})
    )

    items_by_order = (
        order_items.groupby("order_id", as_index=False)
        .agg(
            item_count=("order_item_id", "count"),
            items_gmv=("price", "sum"),
            freight_total=("freight_value", "sum"),
        )
        .copy()
    )

    fact_orders = orders.merge(revenue_by_order, on="order_id", how="left").merge(items_by_order, on="order_id", how="left")

    fact_orders["revenue"] = fact_orders["revenue"].fillna(0.0)
    fact_orders["item_count"] = fact_orders["item_count"].fillna(0).astype(int)
    fact_orders["items_gmv"] = fact_orders["items_gmv"].fillna(0.0)
    fact_orders["freight_total"] = fact_orders["freight_total"].fillna(0.0)

    # Delivery metrics (days)
    delivered = fact_orders["order_delivered_customer_date"]
    purchased = fact_orders["order_purchase_timestamp"]
    estimated = fact_orders["order_estimated_delivery_date"]

    fact_orders["delivery_days"] = (delivered - purchased).dt.total_seconds() / (24 * 3600)
    fact_orders["delay_days"] = (delivered - estimated).dt.total_seconds() / (24 * 3600)
    fact_orders["is_late"] = np.where(fact_orders["delay_days"].notna(), (fact_orders["delay_days"] > 0).astype(int), np.nan)

    # Select/Order columns for Power BI
    fact_orders_cols = [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "revenue",
        "item_count",
        "items_gmv",
        "freight_total",
        "delivery_days",
        "delay_days",
        "is_late",
    ]
    fact_orders = fact_orders[[c for c in fact_orders_cols if c in fact_orders.columns]].drop_duplicates(subset=["order_id"])

    fact_order_items_cols = [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
    ]
    fact_order_items = order_items[[c for c in fact_order_items_cols if c in order_items.columns]].copy()

    fact_reviews = reviews.copy()
    # Add delivery context for analysis in Power BI (optional but very useful)
    if "order_id" in fact_reviews.columns:
        fact_reviews = fact_reviews.merge(
            fact_orders[["order_id", "delivery_days", "delay_days", "is_late"]],
            on="order_id",
            how="left",
        )

    fact_reviews_cols = [
        "review_id",
        "order_id",
        "review_score",
        "review_creation_date",
        "review_answer_timestamp",
        "delivery_days",
        "delay_days",
        "is_late",
    ]
    # Keep comment fields out of the core mart (large text) unless you explicitly want them in Power BI
    fact_reviews = fact_reviews[[c for c in fact_reviews_cols if c in fact_reviews.columns]].drop_duplicates()

    # ---- Dimensions
    dim_customers_cols = [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ]
    dim_customers = customers[[c for c in dim_customers_cols if c in customers.columns]].drop_duplicates(subset=["customer_id"])

    dim_products_cols = [
        "product_id",
        "product_category_name",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
        "product_name_lenght",
        "product_description_lenght",
    ]
    dim_products = products[[c for c in dim_products_cols if c in products.columns]].drop_duplicates(subset=["product_id"])

    dim_sellers_cols = [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ]
    dim_sellers = sellers[[c for c in dim_sellers_cols if c in sellers.columns]].drop_duplicates(subset=["seller_id"])

    # ---- Date dimension (based on purchase timestamp)
    dim_date = _build_dim_date(
        min_dt=fact_orders["order_purchase_timestamp"].min(),
        max_dt=fact_orders["order_purchase_timestamp"].max(),
    )

    # ---- Export
    exports: list[tuple[str, pd.DataFrame]] = [
        ("fact_orders.csv", fact_orders),
        ("fact_order_items.csv", fact_order_items),
        ("fact_reviews.csv", fact_reviews),
        ("dim_customers.csv", dim_customers),
        ("dim_products.csv", dim_products),
        ("dim_sellers.csv", dim_sellers),
        ("dim_date.csv", dim_date),
    ]

    for fname, df in exports:
        out = paths.powerbi_dir / fname
        df.to_csv(out, index=False)

    # Minimal run summary
    summary = {fname: int(df.shape[0]) for fname, df in exports}
    print("Power BI mart exported to:", paths.powerbi_dir)
    for k, v in summary.items():
        print(f"- {k}: {v:,} rows")


if __name__ == "__main__":
    build_powerbi_mart()

