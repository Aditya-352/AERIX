from __future__ import annotations
from analytics.quality import quality_summary, iqr_flags, robust_mad_flags
class DataCleaningPipeline:
    @staticmethod
    def clean(records:list[dict])->list[dict]:
        eligible=[dict(r) for r in records if r.get('collection_status','SUCCESS')=='SUCCESS' and r.get('availability_status','AVAILABLE') not in ('SOLD_OUT','CANCELLED') and r.get('total_fare') is not None and float(r['total_fare'])>0]
        groups={}
        for r in eligible:groups.setdefault((r.get('origin'),r.get('destination'),r.get('travel_date')),[]).append(r)
        for _,group in groups.items():
            vals=[float(x['total_fare']) for x in group]; fi=iqr_flags(vals);fm=robust_mad_flags(vals)
            for row,a,b in zip(group,fi,fm):row['outlier_flag']=bool(a or b);row['quality_score']=0 if row['outlier_flag'] else 100
        return [r for r in eligible if not r.get('outlier_flag',False)]
    @staticmethod
    def compute_quality_metrics(records:list[dict],attempted:int|None=None):return quality_summary(records,attempted)

    @staticmethod
    def detect_outliers_iqr(fares, iqr_factor=1.5):
        return iqr_flags(list(fares),iqr_factor)
    @staticmethod
    def detect_outliers_mad(fares,mad_threshold=3.0):
        return robust_mad_flags(list(fares),mad_threshold)
