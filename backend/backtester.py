import numpy as np
from typing import List, Dict, Optional
from models import BacktestResult, IndexValue
from scraper.dgca_fetcher import fetch_benchmark_series, BenchmarkFetchError

class IndexBacktester:
    @staticmethod
    def run_backtest(
        index_series: List[IndexValue],
        annexure_xlsx_url: Optional[str] = None,
    ) -> BacktestResult:
        """
        Perform backtesting comparison of APIx against a REAL external benchmark
        (CPI 'Transport and communication' sub-group 6.1.03, sourced from
        MoSPI's monthly Annexure I release — see scraper/dgca_fetcher.py for
        the full sourcing rationale, base-year note, and the one remaining
        manual verification step before this is fully trustworthy).
        Computes MAE, RMSE, and Pearson Correlation coefficient.

        PREVIOUS VERSION generated its "benchmark" via
        `bench = apix_value * 0.995 + noise`, i.e. comparing APIx against a
        noised copy of itself. That guarantees a high correlation regardless
        of whether APIx tracks reality — it is not a valid backtest. This
        version requires a real fetched series and raises rather than
        silently reverting to that pattern if one isn't available.

        NOTE: this signature previously took api_key/resource_id (aimed at
        a data.gov.in API that turned out not to exist for this dataset —
        see dgca_fetcher.py's revision history). It now takes a direct
        Annexure I .xlsx URL instead, matching the real, verified source.
        """
        if not index_series:
            raise ValueError(
                "Cannot backtest an empty index series. This previously "
                "returned hardcoded placeholder numbers (apix_mean=107.5, "
                "pearson_correlation=0.978, etc.) — raising here instead "
                "because a caller silently getting fake-but-plausible "
                "results is worse than an explicit error to handle."
            )

        apix_vals = [pt.index_value for pt in index_series]
        dates = [pt.period for pt in index_series]

        try:
            benchmark_map = fetch_benchmark_series(
                start_date=dates[0], end_date=dates[-1],
                annexure_xlsx_url=annexure_xlsx_url,
            )
        except BenchmarkFetchError as e:
            raise BenchmarkFetchError(
                f"Cannot run a real backtest without a real benchmark: {e}\n"
                f"This error is intentional — see backtester.py docstring. "
                f"Do not catch this and substitute synthetic values; that "
                f"recreates the exact problem this rewrite fixes."
            ) from e

        # Only compare dates present in both series — do not silently fill
        # missing benchmark dates with APIx's own value (that would
        # reintroduce self-comparison for those points).
        matched_dates = [d for d in dates if d in benchmark_map]
        if len(matched_dates) < 2:
            raise BenchmarkFetchError(
                f"Only {len(matched_dates)} dates overlap between APIx "
                f"({dates[0]} to {dates[-1]}) and the fetched benchmark. "
                f"Need at least 2 for a meaningful correlation. Check that "
                f"the benchmark's date format and range actually match — "
                f"CPI is typically monthly, so a daily APIx series may need "
                f"forward-filling the monthly value across days in that month, "
                f"not a 1:1 date match. Adjust the matching logic here once "
                f"you've inspected a real fetched response."
            )

        apix_vals = [pt.index_value for pt in index_series if pt.period in matched_dates]
        dates = matched_dates
        benchmark_vals = [benchmark_map[d] for d in matched_dates]

        apix_arr = np.array(apix_vals)
        bench_arr = np.array(benchmark_vals)

        mae = float(np.mean(np.abs(apix_arr - bench_arr)))
        rmse = float(np.sqrt(np.mean((apix_arr - bench_arr) ** 2)))
        
        # Pearson Correlation
        if len(apix_arr) > 1 and np.std(apix_arr) > 0 and np.std(bench_arr) > 0:
            corr = float(np.corrcoef(apix_arr, bench_arr)[0, 1])
        else:
            corr = 1.0

        data_pts = []
        for d, a_v, b_v in zip(dates, apix_vals, benchmark_vals):
            data_pts.append({
                "date": d,
                "apix": a_v,
                "benchmark": b_v,
                "diff": round(a_v - b_v, 2)
            })

        return BacktestResult(
            start_date=dates[0],
            end_date=dates[-1],
            routes_count=10,
            apix_mean=round(float(np.mean(apix_arr)), 2),
            benchmark_mean=round(float(np.mean(bench_arr)), 2),
            mae=round(mae, 3),
            rmse=round(rmse, 3),
            pearson_correlation=round(corr, 4),
            data_points=data_pts
        )
