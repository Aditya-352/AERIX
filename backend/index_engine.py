from typing import List, Dict
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from models import (
    RouteBasketItem, IndexValue, LeadTimePoint, HeatmapItem,
    AirlineMetric, OTAMetric, CleanedObservation
)
from synthetic_engine import DEFAULT_ROUTES

class AirfareIndexEngine:
    def __init__(self, observations: List[CleanedObservation]):
        self.observations = observations
        self.df = pd.DataFrame([o.model_dump() for o in observations])
        self.routes = self._init_route_basket()

    def _init_route_basket(self) -> List[RouteBasketItem]:
        basket = []
        total_share = sum(r["share"] for r in DEFAULT_ROUTES)

        for r in DEFAULT_ROUTES:
            weight = r["share"] / total_share
            route_obs = self.df[self.df["route_id"] == r["route_id"]] if not self.df.empty else pd.DataFrame()
            avg_f = float(route_obs["total_fare"].mean()) if not route_obs.empty else float(r["base_price"])

            basket.append(RouteBasketItem(
                route_id=r["route_id"],
                origin=r["origin"],
                destination=r["destination"],
                origin_name=r["origin_name"],
                destination_name=r["destination_name"],
                passenger_traffic_annual=int(r["share"] * 100_000_000),
                traffic_share=round(r["share"] * 100, 2),
                weight=round(weight, 4),
                enabled=True,
                total_observations=len(route_obs),
                avg_fare=round(avg_f, 2)
            ))
        return basket

    def get_route_basket(self) -> List[RouteBasketItem]:
        return self.routes

    def calculate_index_series(self) -> List[IndexValue]:
        """
        Calculate daily weighted Airfare Price Index (APIx) over time.
        Base Index = 100.0 (Base Period = Jan 2026).
        """
        if self.df.empty:
            return []

        # Exclude flagged outliers from index calculation
        clean_df = self.df[self.df["outlier_flag"] == False]

        # Group by observation date and route
        daily_route_means = clean_df.groupby(["observation_timestamp", "route_id"])["total_fare"].mean().reset_index()

        weights_map = {r.route_id: r.weight for r in self.routes}
        dates = sorted(daily_route_means["observation_timestamp"].unique())

        if not dates:
            return []

        # Establish base fares per route from earliest date (Jan 2026 reference ~ Aug 5 start date)
        first_date = dates[0]
        base_fares = daily_route_means[daily_route_means["observation_timestamp"] == first_date].set_index("route_id")["total_fare"].to_dict()

        base_weighted_sum = sum(weights_map.get(rid, 0.1) * fare for rid, fare in base_fares.items())
        if base_weighted_sum == 0:
            base_weighted_sum = 1.0

        index_series = []
        prev_idx = 100.0

        for idx, d in enumerate(dates):
            day_data = daily_route_means[daily_route_means["observation_timestamp"] == d]
            current_fares = day_data.set_index("route_id")["total_fare"].to_dict()

            current_weighted_sum = sum(weights_map.get(rid, 0.1) * current_fares.get(rid, base_fares.get(rid, 5000)) for rid in weights_map)
            
            # APIx index formula: (Current Weighted Sum / Base Weighted Sum) * 100
            idx_val = round((current_weighted_sum / base_weighted_sum) * 100.0, 2)

            daily_change = round(((idx_val - prev_idx) / prev_idx) * 100.0, 2) if idx > 0 else 0.0

            # Calculate 7-day and 30-day changes
            idx_7d_ago = index_series[max(0, idx - 7)].index_value if index_series else 100.0
            weekly_change = round(((idx_val - idx_7d_ago) / idx_7d_ago) * 100.0, 2)

            idx_30d_ago = index_series[0].index_value if index_series else 100.0
            monthly_change = round(((idx_val - idx_30d_ago) / idx_30d_ago) * 100.0, 2)

            index_series.append(IndexValue(
                period=d,
                index_value=idx_val,
                base_period="2026-01",
                base_index=100.0,
                daily_change_pct=daily_change,
                weekly_change_pct=weekly_change,
                monthly_change_pct=monthly_change,
                total_routes=len(self.routes),
                total_observations=len(clean_df[clean_df["observation_timestamp"] == d]),
                methodology_version="1.0"
            ))
            prev_idx = idx_val

        return index_series

    def get_lead_time_elasticity(self, route_id: str = None) -> List[LeadTimePoint]:
        """Calculate Lead-Time Elasticity Curve (T+1, T+7, T+15, T+30, T+45)."""
        clean_df = self.df[self.df["outlier_flag"] == False]
        if route_id:
            clean_df = clean_df[clean_df["route_id"] == route_id]

        points = []
        windows = [(1, "T+1"), (7, "T+7"), (15, "T+15"), (30, "T+30"), (45, "T+45")]

        for days, label in windows:
            sub = clean_df[clean_df["lead_time"] == days]
            avg_fare = float(sub["total_fare"].mean()) if not sub.empty else 5000.0

            indigo = float(sub[sub["airline"] == "IndiGo"]["total_fare"].mean()) if not sub[sub["airline"] == "IndiGo"].empty else avg_fare * 0.98
            airindia = float(sub[sub["airline"] == "Air India"]["total_fare"].mean()) if not sub[sub["airline"] == "Air India"].empty else avg_fare * 1.05
            akasa = float(sub[sub["airline"] == "Akasa Air"]["total_fare"].mean()) if not sub[sub["airline"] == "Akasa Air"].empty else avg_fare * 0.92
            spicejet = float(sub[sub["airline"] == "SpiceJet"]["total_fare"].mean()) if not sub[sub["airline"] == "SpiceJet"].empty else avg_fare * 0.95

            points.append(LeadTimePoint(
                lead_time=label,
                days=days,
                avg_fare=round(avg_fare, 2),
                indigo_fare=round(indigo, 2),
                airindia_fare=round(airindia, 2),
                akasa_fare=round(akasa, 2),
                spicejet_fare=round(spicejet, 2)
            ))
        return points

    def get_route_heatmap_data(self) -> List[HeatmapItem]:
        """Generate geographic route fare changes for heatmap visualization."""
        clean_df = self.df[self.df["outlier_flag"] == False]
        heatmap = []

        weights_map = {r.route_id: r.weight for r in self.routes}

        for r in DEFAULT_ROUTES:
            rid = r["route_id"]
            sub = clean_df[clean_df["route_id"] == rid]
            if sub.empty:
                continue

            dates = sorted(sub["observation_timestamp"].unique())
            if len(dates) < 2:
                latest_avg = float(sub["total_fare"].mean())
                prev_avg = latest_avg
            else:
                latest_avg = float(sub[sub["observation_timestamp"] == dates[-1]]["total_fare"].mean())
                prev_avg = float(sub[sub["observation_timestamp"] == dates[-7] if len(dates) >= 7 else dates[0]]["total_fare"].mean())

            chg_pct = round(((latest_avg - prev_avg) / prev_avg) * 100.0, 2) if prev_avg > 0 else 0.0

            if chg_pct > 5.0:
                intensity = "HIGH_INCREASE"
            elif chg_pct > 0.0:
                intensity = "MODERATE_INCREASE"
            elif chg_pct > -3.0:
                intensity = "STABLE"
            else:
                intensity = "DECREASE"

            heatmap.append(HeatmapItem(
                route_id=rid,
                origin=r["origin"],
                destination=r["destination"],
                current_avg_fare=round(latest_avg, 2),
                prev_avg_fare=round(prev_avg, 2),
                change_pct=chg_pct,
                traffic_weight=weights_map.get(rid, 0.05),
                intensity=intensity
            ))
        return heatmap

    def get_airline_analytics(self) -> List[AirlineMetric]:
        """Generate airline level pricing and volatility analytics."""
        clean_df = self.df[self.df["outlier_flag"] == False]
        metrics = []

        for airline_name in clean_df["airline"].unique():
            sub = clean_df[clean_df["airline"] == airline_name]
            fares = sub["total_fare"]

            avg_f = float(fares.mean())
            med_f = float(fares.median())
            min_f = float(fares.min())
            max_f = float(fares.max())
            std_f = float(fares.std())
            volatility_pct = round((std_f / avg_f) * 100.0, 2) if avg_f > 0 else 0.0

            vol_label = "Low" if volatility_pct < 8.0 else ("Medium" if volatility_pct < 15.0 else "High")
            code_map = {"IndiGo": "6E", "Air India": "AI", "Akasa Air": "QP", "SpiceJet": "SG", "Air India Express": "IX"}

            metrics.append(AirlineMetric(
                airline_name=airline_name,
                code=code_map.get(airline_name, "XX"),
                avg_fare=round(avg_f, 2),
                median_fare=round(med_f, 2),
                cheapest_fare=round(min_f, 2),
                highest_fare=round(max_f, 2),
                volatility=vol_label,
                volatility_score=volatility_pct,
                route_coverage=sub["route_id"].nunique()
            ))
        return metrics

    def get_ota_analytics(self) -> List[OTAMetric]:
        """Generate OTA provider comparison analytics."""
        clean_df = self.df[self.df["outlier_flag"] == False]
        metrics = []

        direct_avg = float(clean_df[clean_df["provider_id"] == "DIRECT"]["total_fare"].mean()) if not clean_df[clean_df["provider_id"] == "DIRECT"].empty else 5000.0

        for pid in clean_df["provider_id"].unique():
            sub = clean_df[clean_df["provider_id"] == pid]
            prov_avg = float(sub["total_fare"].mean())
            fee_avg = float(sub["fees"].mean())
            diff_pct = round(((prov_avg - direct_avg) / direct_avg) * 100.0, 2) if direct_avg > 0 else 0.0
            pname = sub["provider_id"].iloc[0]

            metrics.append(OTAMetric(
                provider_name=pname,
                avg_price_diff_pct=diff_pct,
                availability_rate=98.8,
                fee_avg=round(fee_avg, 2),
                fare_consistency_score=round(100.0 - abs(diff_pct) * 2.5, 1)
            ))
        return metrics
