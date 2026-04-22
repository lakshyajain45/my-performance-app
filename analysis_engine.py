import pandas as pd
import numpy as np

class AnalysisEngine:
    @staticmethod
    def load_data(file):
        """Loads CSV or Excel files."""
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            return df
        except Exception as e:
            return str(e)

    @staticmethod
    def get_summary_stats(df, metric_col):
        """Calculates core KPIs for a specific metric."""
        if not pd.api.types.is_numeric_dtype(df[metric_col]):
            return None
        
        stats = {
            "Total": df[metric_col].sum(),
            "Average": df[metric_col].mean(),
            "Max": df[metric_col].max(),
            "Min": df[metric_col].min(),
            "Count": len(df)
        }
        return stats

    @staticmethod
    def get_top_performers(df, category_col, metric_col, top_n=5):
        """Groups data by category and finds top performers."""
        grouped = df.groupby(category_col)[metric_col].sum().sort_values(ascending=False)
        return grouped.head(top_n), grouped.tail(top_n)

    @staticmethod
    def detect_anomalies(df, metric_col):
        """Simple Z-score based anomaly detection."""
        mean = df[metric_col].mean()
        std = df[metric_col].std()
        threshold = 3
        
        anomalies = df[np.abs(df[metric_col] - mean) > (threshold * std)]
        return anomalies
