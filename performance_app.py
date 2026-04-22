import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
try:
    from src.analysis_engine import AnalysisEngine
except ImportError:
    from analysis_engine import AnalysisEngine

# Page Config
st.set_page_config(page_title="Performance Analyzer Pro", layout="wide", page_icon="📈")

# Custom Styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #3d425b;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("📊 Data-Driven Performance Analyzer")
    st.markdown("---")

    # 1. Sidebar - Data Upload
    with st.sidebar:
        st.header("Setup")
        uploaded_file = st.file_uploader("Upload your Data (CSV or Excel)", type=['csv', 'xlsx'])
        
        df = None
        if uploaded_file:
            df = AnalysisEngine.load_data(uploaded_file)
        elif "sample_df" in st.session_state:
            df = st.session_state.sample_df

        if df is not None:
            if isinstance(df, str):
                st.error(f"Error loading file: {df}")
                return
            
            st.success("Data Loaded Successfully!")
            
            # Column Selectors
            all_cols = df.columns.tolist()
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            st.markdown("---")
            metric_to_analyze = st.selectbox("Select Metric to Analyze", numeric_cols)
            category_col = st.selectbox("Select Category (Group By)", all_cols)
            date_col = st.selectbox("Select Date Column (Optional)", ["None"] + all_cols)

    # 2. Main Dashboard
    if df is None:
        st.info("👋 Welcome! Please upload a data file in the sidebar to start analyzing performance.")
        
        # Sample Data Button
        if st.button("Generate & Load Sample Data"):
            st.session_state.sample_df = pd.DataFrame({
                'Employee': ['Rahul', 'Anjali', 'Vikram', 'Sonia', 'Karan', 'Priya'],
                'Sales': [4500, 3200, 5100, 2800, 6000, 3900],
                'Date': pd.date_range(start='2024-01-01', periods=6, freq='ME')
            })
            st.rerun()
    
    else:
        # Performance Summary Cards
        stats = AnalysisEngine.get_summary_stats(df, metric_to_analyze)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", f"{stats['Total']:,.0f}")
        with col2:
            st.metric("Average", f"{stats['Average']:,.2f}")
        with col3:
            st.metric("Max", f"{stats['Max']:,.0f}")
        with col4:
            st.metric("Sample Size", stats['Count'])

        st.markdown("---")

        # Visuals Row 1
        v_col1, v_col2 = st.columns(2)
        
        with v_col1:
            st.subheader(f"Top 5 Performers by {category_col}")
            top, bottom = AnalysisEngine.get_top_performers(df, category_col, metric_to_analyze)
            fig_top = px.bar(top, orientation='h', color=top.values, color_continuous_scale='Viridis')
            st.plotly_chart(fig_top, use_container_width=True)

        with v_col2:
            st.subheader(f"Distribution of {metric_to_analyze}")
            fig_dist = px.histogram(df, x=metric_to_analyze, marginal="box", nbins=20, color_discrete_sequence=['#4CAF50'])
            st.plotly_chart(fig_dist, use_container_width=True)

        # Visuals Row 2 (Time Series if date is selected)
        if date_col != "None":
            st.markdown("---")
            st.subheader(f"Performance Trend Over Time ({date_col})")
            df[date_col] = pd.to_datetime(df[date_col])
            trend_df = df.groupby(date_col)[metric_to_analyze].sum().reset_index()
            fig_trend = px.line(trend_df, x=date_col, y=metric_to_analyze, markers=True)
            st.plotly_chart(fig_trend, use_container_width=True)

        # AI Insights Section
        st.markdown("---")
        with st.expander("💡 Smart Performance Insights", expanded=True):
            anomalies = AnalysisEngine.detect_anomalies(df, metric_to_analyze)
            
            st.markdown(f"**Quick Summary:**")
            st.write(f"- The top performer in **{category_col}** is **{top.index[0]}** with a total of **{top.iloc[0]:,.0f}**.")
            st.write(f"- The average **{metric_to_analyze}** across all categories is **{stats['Average']:,.2f}**.")
            
            if not anomalies.empty:
                st.warning(f"Detected **{len(anomalies)}** potential anomalies (unusual performance spikes or drops).")
                st.dataframe(anomalies)
            else:
                st.success("No extreme anomalies detected. Performance is consistent within the expected range.")

if __name__ == "__main__":
    main()
