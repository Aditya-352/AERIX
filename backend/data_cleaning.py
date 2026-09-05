import numpy as np
from typing import List, Tuple
from models import CleanedObservation

class DataCleaningPipeline:
    @staticmethod
    def detect_outliers_iqr(fares: List[float], iqr_factor: float = 1.5) -> List[bool]:
        """Detect outliers using Interquartile Range (IQR) method."""
        if not fares or len(fares) < 4:
            return [False] * len(fares)

        q25, q75 = np.percentile(fares, [25, 75])
        iqr = q75 - q25
        lower_bound = q25 - (iqr_factor * iqr)
        upper_bound = q75 + (iqr_factor * iqr)

        return [fare < lower_bound or fare > upper_bound for fare in fares]

    @staticmethod
    def detect_outliers_mad(fares: List[float], mad_threshold: float = 3.0) -> List[bool]:
        """Detect outliers using Median Absolute Deviation (MAD) method."""
        if not fares or len(fares) < 4:
            return [False] * len(fares)

        median = np.median(fares)
        mad = np.median(np.abs(fares - median))
        if mad == 0:
            return [False] * len(fares)

        modified_z_scores = 0.6745 * np.abs(fares - median) / mad
        return [score > mad_threshold for score in modified_z_scores]

    @staticmethod
    def deduplicate_observations(observations: List[CleanedObservation]) -> List[CleanedObservation]:
        """
        Deduplicate observations matching the exact same flight, provider, travel_date, and timestamp.
        Keep highest quality score record.
        """
        seen = {}
        for obs in observations:
            key = (obs.flight_id, obs.provider_id, obs.travel_date, obs.observation_timestamp)
            if key not in seen or obs.quality_score > seen[key].quality_score:
                seen[key] = obs
        return list(seen.values())

    @staticmethod
    def compute_quality_metrics(observations: List[CleanedObservation]) -> dict:
        total = len(observations)
        if total == 0:
            # PRE-EXISTING BUG (not introduced by this edit): this branch was
            # missing "last_updated", which DataQualityMetrics requires — it
            # was latent because dataset_engine.cleaned_observations is never
            # actually empty in the current synthetic setup, so this path was
            # never exercised. Fixed here since it's now required either way.
            return {
                "overall_score": 100.0,
                "completeness": 100.0,
                "duplicate_rate": 0.0,
                "missing_fare_rate": 0.0,
                "outlier_rate": 0.0,
                "collection_success_rate": None,
                "last_updated": "N/A — no observations"
            }

        outliers = sum(1 for o in observations if o.outlier_flag)
        missing_fares = sum(1 for o in observations if o.total_fare <= 0)
        invalid_quality = sum(1 for o in observations if o.quality_score < 70)

        outlier_rate = round((outliers / total) * 100, 2)
        missing_fare_rate = round((missing_fares / total) * 100, 2)

        # PREVIOUSLY hardcoded to 1.2 with comment "calculated from
        # deduplication step" — it was not actually calculated anywhere.
        # deduplicate_observations() (above in this same file) already does
        # the real work; it was just never called. Now it is.
        deduped = DataCleaningPipeline.deduplicate_observations(observations)
        duplicates_removed = total - len(deduped)
        duplicate_rate = round((duplicates_removed / total) * 100, 2)

        completeness = round(100.0 - missing_fare_rate - 0.5, 1)

        # PREVIOUSLY hardcoded to 96.5 with no computation. Real collection
        # success rate needs a numerator this function does not receive today
        # (attempted-vs-succeeded counts from the scraper job, not the
        # cleaned observations themselves). Rather than invent a formula OR
        # pass None (which breaks DataQualityMetrics' `float` field — see
        # models.py), return -1.0 as an explicit "not yet measurable" sentinel
        # and surface it honestly in the API response instead of a silent
        # constant. Replace with a real computation once
        # scraper/flight_scraper_poc.py's run_scrape_job() is producing real
        # attempt/success counts to pass in here.
        collection_success_rate = -1.0

        overall_score = round(100.0 - (outlier_rate * 1.2 + missing_fare_rate * 3.0 + duplicate_rate * 0.5), 1)

        return {
            "overall_score": max(overall_score, 0.0),
            "completeness": min(completeness, 100.0),
            "duplicate_rate": duplicate_rate,
            "missing_fare_rate": missing_fare_rate,
            "outlier_rate": outlier_rate,
            "collection_success_rate": collection_success_rate,
            "last_updated": "2026-09-04 23:00:00"
        }
