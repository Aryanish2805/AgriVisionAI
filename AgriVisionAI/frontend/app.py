import html
import sys
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from ml_model.crop_recommender import recommend_from_record
from ml_model.evaluate import evaluate_model


BASE_DIR = Path(__file__).resolve().parents[1]
DATASET_DIR = BASE_DIR / "dataset"
REPORT_PATH = BASE_DIR / "reports" / "model_evaluation.txt"


st.set_page_config(
    page_title="AI-Based Crop Recommendation System",
    page_icon="🌾",
    layout="wide",
)


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --av-accent: #15803d;
            --av-accent-strong: #166534;
            --av-accent-soft: rgba(34, 197, 94, 0.14);
            --av-border: rgba(34, 197, 94, 0.26);
            --av-shadow: rgba(15, 23, 42, 0.10);
            --av-muted: color-mix(in srgb, var(--text-color) 68%, transparent);
            --av-panel: color-mix(in srgb, var(--secondary-background-color) 92%, transparent);
            --av-panel-soft: color-mix(in srgb, var(--secondary-background-color) 72%, var(--background-color));
        }}

        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(34, 197, 94, 0.10), transparent 28%),
                radial-gradient(circle at top right, rgba(21, 128, 61, 0.08), transparent 26%),
                var(--background-color);
            color: var(--text-color);
        }}

        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stHeader"],
        .main, .appview-container {{
            background: transparent !important;
            color: var(--text-color) !important;
        }}

        ::selection {{
            background: rgba(22, 163, 74, 0.28);
            color: #ffffff;
        }}

        header[data-testid="stHeader"] {{
            background: transparent !important;
            backdrop-filter: none;
            border-bottom: 0;
        }}

        div[data-testid="stToolbar"] {{
            background: transparent;
        }}

        div[data-testid="stDeployButton"] button,
        .stDeployButton button {{
            background: #15803d !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.18) !important;
            box-shadow: 0 10px 24px rgba(21, 128, 61, 0.24);
            font-weight: 700 !important;
            border-radius: 8px !important;
            padding: 0.45rem 0.75rem !important;
        }}

        div[data-testid="stDeployButton"] button:hover,
        .stDeployButton button:hover {{
            background: #166534 !important;
            color: #ffffff !important;
        }}

        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }}

        h1, h2, h3, h4, h5, h6, p, li, span, label {{
            color: var(--text-color);
        }}

        .panel-card {{
            background: var(--av-panel);
            border: 1px solid var(--av-border);
            border-radius: 8px;
            padding: 1.2rem 1.3rem;
            box-shadow: 0 12px 32px var(--av-shadow);
            backdrop-filter: blur(10px);
        }}

        .hero-card {{
            background: var(--av-panel);
            color: var(--text-color);
            margin-bottom: 1.5rem;
            border: 1px solid var(--av-border);
            border-radius: 8px;
            padding: 1.8rem 1.5rem;
            box-shadow: 0 12px 32px var(--av-shadow);
            text-align: center;
        }}

        .hero-card h1,
        .hero-card p {{
            color: var(--text-color);
            margin: 0 auto;
            line-height: 1.25;
            text-shadow: none;
        }}

        .hero-card h1 {{
            font-size: clamp(2rem, 4vw, 3.2rem);
            font-weight: 800;
            max-width: 840px;
        }}

        .hero-card p {{
            font-size: 1rem;
            font-weight: 500;
            color: var(--av-muted);
            max-width: 720px;
            margin-top: 0.85rem;
        }}

        .eyebrow {{
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.72rem;
            color: var(--av-accent);
            margin-bottom: 0.75rem;
            font-weight: 700;
        }}

        .hero-tags {{
            display: flex;
            justify-content: center;
            gap: 0.55rem;
            flex-wrap: wrap;
            margin-top: 1.15rem;
        }}

        .hero-tag {{
            border: 1px solid var(--av-border);
            border-radius: 999px;
            color: var(--av-muted);
            font-size: 0.82rem;
            font-weight: 650;
            padding: 0.35rem 0.7rem;
            background: color-mix(in srgb, var(--secondary-background-color) 70%, transparent);
        }}

        .section-heading {{
            font-size: 1.05rem;
            font-weight: 700;
            margin: 0.1rem 0 0.35rem 0;
            color: var(--text-color);
        }}

        .section-subtitle {{
            color: var(--av-muted);
            font-size: 0.93rem;
            margin-bottom: 0.85rem;
        }}

        .metric-card {{
            background: linear-gradient(180deg, var(--av-panel), var(--av-panel-soft));
            border: 1px solid var(--av-border);
            border-radius: 8px;
            padding: 0.85rem 0.9rem;
        }}

        .metric-rank {{
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.72rem;
            color: var(--av-muted);
            margin-bottom: 0.2rem;
        }}

        .metric-title {{
            font-size: 1.02rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
            color: var(--text-color);
        }}

        .prob-row {{
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin: 0.45rem 0;
        }}

        .prob-label {{
            width: 110px;
            flex-shrink: 0;
            color: var(--text-color);
            font-size: 0.84rem;
        }}

        .prob-track {{
            flex: 1;
            min-width: 120px;
            height: 12px;
            background: rgba(148, 163, 184, 0.18);
            border-radius: 999px;
            overflow: hidden;
        }}

        .prob-fill {{
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, #22c55e 0%, #15803d 100%);
        }}

        .prob-value {{
            width: 58px;
            text-align: right;
            color: var(--text-color);
            font-size: 0.82rem;
            font-weight: 700;
            flex-shrink: 0;
        }}

        .analysis-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 0.9rem;
        }}

        .heatmap-wrap {{
            overflow-x: auto;
        }}

        .heatmap-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 6px;
            table-layout: fixed;
        }}

        .heatmap-table th,
        .heatmap-table td {{
            padding: 0.6rem 0.5rem;
            border-radius: 8px;
            text-align: center;
            font-size: 0.82rem;
        }}

        .heatmap-table th {{
            color: var(--text-color);
            font-weight: 700;
            background: var(--av-panel);
        }}

        .heatmap-row-label {{
            text-align: left !important;
            padding-left: 0.8rem !important;
            white-space: nowrap;
            color: var(--text-color);
            font-weight: 700;
        }}

        .heatmap-cell {{
            font-weight: 700;
            border: 1px solid var(--av-border);
        }}

        .stButton > button {{
            background: linear-gradient(135deg, var(--av-accent), var(--av-accent-strong));
            color: #ffffff !important;
            border: none;
            border-radius: 8px;
            padding: 0.72rem 1rem;
            font-weight: 700;
            cursor: pointer;
        }}

        .stButton > button:hover {{
            filter: brightness(1.05);
        }}

        div[data-testid="stWidgetLabel"],
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricValue"],
        div[data-testid="stMarkdownContainer"] p,
        .stMarkdown, .stMarkdown p, .stCaption {{
            color: var(--text-color) !important;
        }}

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-baseweb="select"] > div {{
            background-color: var(--secondary-background-color) !important;
            color: var(--text-color) !important;
            border-color: var(--av-border) !important;
        }}

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {{
            -webkit-text-fill-color: var(--text-color) !important;
        }}

        div[data-baseweb="select"] span {{
            color: var(--text-color) !important;
        }}

        input::placeholder {{
            color: var(--av-muted) !important;
            opacity: 1;
        }}

        button[kind="header"] {{
            color: #ffffff !important;
        }}

        .stDataFrame, .stTable {{
            border-radius: 8px;
            overflow: hidden;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


def list_datasets():
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(DATASET_DIR.glob("*.csv"))


def detect_schema(columns):
    lowered = {column.strip().lower(): column for column in columns}
    numeric_schema = {"n", "p", "k", "temperature", "humidity", "ph", "rainfall"}
    if numeric_schema.issubset(lowered):
        return "numeric", lowered
    if "soil_type" in lowered:
        return "soil", lowered
    return "unknown", lowered


def normalize_probability(probability):
    if probability is None:
        return None
    try:
        value = float(probability)
    except (TypeError, ValueError):
        return None
    if value > 1.0 and value <= 100.0:
        value /= 100.0
    return value


def format_probability(probability):
    value = normalize_probability(probability)
    return "N/A" if value is None else f"{value:.1%}"


def normalize_suggestions(result):
    suggestions = []
    if not result:
        return suggestions

    for suggestion in result.get("suggestions") or []:
        crop_name = None
        confidence = None
        if isinstance(suggestion, dict):
            crop_name = suggestion.get("crop") or suggestion.get("name") or suggestion.get("label")
            confidence = suggestion.get("probability")
            if confidence is None:
                confidence = suggestion.get("confidence")
        elif isinstance(suggestion, (list, tuple)) and suggestion:
            crop_name = suggestion[0]
            confidence = suggestion[1] if len(suggestion) > 1 else None
        else:
            crop_name = suggestion
        if crop_name is not None:
            suggestions.append((str(crop_name), normalize_probability(confidence)))

    if not suggestions and result.get("recommended_crop"):
        suggestions.append((str(result.get("recommended_crop")), normalize_probability(result.get("confidence"))))

    return suggestions


def backend_or_local_prediction(record, show_feedback=True):
    try:
        response = requests.post("http://localhost:8000/predict", json=record, timeout=5)
        if response.status_code == 200:
            backend_data = response.json()
            suggestions = []
            for candidate in backend_data.get("candidates") or []:
                if isinstance(candidate, dict):
                    crop_name = candidate.get("crop") or candidate.get("name") or candidate.get("label")
                    probability = candidate.get("probability")
                    if probability is None:
                        probability = candidate.get("confidence")
                    probability = normalize_probability(probability)
                    if crop_name is not None:
                        suggestions.append((str(crop_name), probability))
            if not suggestions and backend_data.get("recommended_crop"):
                suggestions.append((str(backend_data["recommended_crop"]), normalize_probability(backend_data.get("confidence"))))
            return {"type": "backend", "suggestions": suggestions, "message": "Prediction from Backend API"}

        if show_feedback:
            st.error(f"Backend API Error: {response.text}")
    except requests.exceptions.RequestException:
        if show_feedback:
            st.warning("Backend API is unreachable. Falling back to local model.")

    local_result = recommend_from_record(record)
    local_result.setdefault("message", "Prediction from local model fallback")
    return local_result


def render_probability_distribution(suggestions):
    filtered = []
    for crop_name, probability in suggestions:
        normalized = normalize_probability(probability)
        if normalized is not None:
            filtered.append((crop_name, normalized))

    if len(filtered) < 2:
        return

    st.markdown("<div class='section-heading'>Candidate probability distribution</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Horizontal comparison of the strongest candidate crops.</div>", unsafe_allow_html=True)
    max_probability = max(probability for _, probability in filtered)
    if max_probability <= 0:
        max_probability = 1.0

    for crop_name, probability in filtered:
        width_pct = max(4.0, (probability / max_probability) * 100.0)
        st.markdown(
            f"""
            <div class="prob-row">
                <div class="prob-label">{html.escape(str(crop_name))}</div>
                <div class="prob-track"><div class="prob-fill" style="width:{width_pct:.2f}%;"></div></div>
                <div class="prob-value">{probability:.1%}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def display_recommendation(result, title="Recommendation"):
    suggestions = normalize_suggestions(result)
    if not suggestions:
        st.info((result or {}).get("message", "No suggestion available"))
        return

    top_crop, top_prob = suggestions[0]
    st.markdown(
        f"<div class='panel-card'><div class='eyebrow'>{html.escape(title)}</div><div class='section-heading'>Top recommendation</div></div>",
        unsafe_allow_html=True,
    )
    metric_left, metric_right = st.columns([2, 1])
    with metric_left:
        st.metric("Recommended crop", top_crop)
    with metric_right:
        st.metric("Confidence", format_probability(top_prob))

    st.markdown("<div class='section-heading'>Recommendation cards</div>", unsafe_allow_html=True)
    card_columns = st.columns(min(3, len(suggestions)))
    for index, (crop_name, probability) in enumerate(suggestions[: len(card_columns)]):
        with card_columns[index]:
            st.markdown(
                f"""
                    <div class="metric-card">
                        <div class="metric-rank">Rank {index + 1}</div>
                        <div class="metric-title">{html.escape(str(crop_name))}</div>
                    <div style="color:var(--av-muted);font-size:0.88rem;">Confidence</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.metric("Score", format_probability(probability))

    if len(suggestions) > 1:
        render_probability_distribution(suggestions)

    if result.get("message"):
        st.caption(result["message"])


def histogram_summary(series, bins=8):
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return None
    bin_count = min(bins, max(2, len(values)))
    categories = pd.cut(values, bins=bin_count, duplicates="drop")
    counts = categories.value_counts().sort_index()
    frame = pd.DataFrame({"bin": [str(interval) for interval in counts.index], "count": counts.values}).set_index("bin")
    return frame


def color_from_value(value):
    value = max(-1.0, min(1.0, float(value)))
    intensity = 0.12 + abs(value) * 0.72
    if value >= 0:
        return f"rgba(22, 163, 74, {intensity:.2f})", "#ffffff" if abs(value) >= 0.55 else "#0f172a"
    return f"rgba(220, 38, 38, {intensity:.2f})", "#ffffff" if abs(value) >= 0.55 else "#0f172a"


def render_dataset_analysis(df):
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        return

    with st.expander("📊 Dataset Insights (Click to expand)", expanded=False):
        st.markdown("<div class='section-subtitle'>Feature statistics and correlations for numeric columns.</div>", unsafe_allow_html=True)
        
        dist_columns = list(numeric_df.columns)[:4]
        if dist_columns:
            cols = st.columns(len(dist_columns))
            for idx, column_name in enumerate(dist_columns):
                with cols[idx]:
                    st.metric(column_name, f"{numeric_df[column_name].mean():.1f}")
                    st.caption(f"Mean: {numeric_df[column_name].mean():.2f}")

        if len(numeric_df.columns) > 1:
            corr = numeric_df.corr().round(2)
            st.markdown("<div class='section-heading'>Correlation Matrix</div>", unsafe_allow_html=True)
            st.dataframe(corr, use_container_width=True)


def render_numeric_input_panel(prefix, schema_map, defaults=None):
    defaults = defaults or {}
    st.markdown(
        f"""
        <div class="panel-card">
            <div class="eyebrow">{html.escape(prefix.replace('_', ' ').title())}</div>
            <div class="section-heading">Input panel</div>
            <div class="section-subtitle">Enter the agronomic values for this scenario.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    row1 = st.columns(3)
    row2 = st.columns(3)
    row3 = st.columns(2)

    nitrogen = row1[0].number_input("Nitrogen (N)", min_value=0.0, max_value=300.0, value=float(defaults.get("N", 50.0)), key=f"{prefix}_n")
    phosphorus = row1[1].number_input("Phosphorus (P)", min_value=0.0, max_value=300.0, value=float(defaults.get("P", 50.0)), key=f"{prefix}_p")
    potassium = row1[2].number_input("Potassium (K)", min_value=0.0, max_value=300.0, value=float(defaults.get("K", 50.0)), key=f"{prefix}_k")
    temperature = row2[0].number_input("Temperature (°C)", min_value=-10.0, max_value=60.0, value=float(defaults.get("temperature", 25.0)), key=f"{prefix}_temperature")
    humidity = row2[1].number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=float(defaults.get("humidity", 70.0)), key=f"{prefix}_humidity")
    ph = row2[2].number_input("Soil pH", min_value=0.0, max_value=14.0, value=float(defaults.get("ph", 6.5)), key=f"{prefix}_ph")
    rainfall = row3[0].number_input("Rainfall", min_value=0.0, max_value=500.0, value=float(defaults.get("rainfall", 100.0)), key=f"{prefix}_rainfall")
    location = row3[1].text_input("Location (optional)", value=str(defaults.get("location", "")), key=f"{prefix}_location")

    record = {
        schema_map["n"]: nitrogen,
        schema_map["p"]: phosphorus,
        schema_map["k"]: potassium,
        schema_map["temperature"]: temperature,
        schema_map["humidity"]: humidity,
        schema_map["ph"]: ph,
        schema_map["rainfall"]: rainfall,
    }
    if location:
        record["location"] = location
    return record


def render_soil_input_panel(prefix, schema_map, defaults=None):
    defaults = defaults or {}
    st.markdown(
        f"""
        <div class="panel-card">
            <div class="eyebrow">{html.escape(prefix.replace('_', ' ').title())}</div>
            <div class="section-heading">Input panel</div>
            <div class="section-subtitle">Enter the soil and weather profile for this scenario.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    soils = ["Loamy", "Sandy", "Clay", "Silty", "Peaty", "Chalky"]
    row1 = st.columns(3)
    row2 = st.columns(2)

    location = row1[0].text_input("Location (optional)", value=str(defaults.get("location", "")), key=f"{prefix}_location")
    soil_default = defaults.get("soil_type", soils[0])
    if soil_default not in soils:
        soil_default = soils[0]
    soil_type = row1[1].selectbox("Soil type", soils, index=soils.index(soil_default), key=f"{prefix}_soil_type")
    rainfall_mm = row1[2].number_input("Estimated rainfall (mm)", min_value=0.0, max_value=500.0, value=float(defaults.get("rainfall_mm", 120.0)), key=f"{prefix}_rainfall_mm")
    temperature_c = row2[0].number_input("Average temperature (°C)", min_value=-10.0, max_value=60.0, value=float(defaults.get("temperature_c", 25.0)), key=f"{prefix}_temperature_c")
    humidity_pct = row2[1].number_input("Relative humidity (%)", min_value=0.0, max_value=100.0, value=float(defaults.get("humidity_pct", 60.0)), key=f"{prefix}_humidity_pct")

    record = {
        schema_map["soil_type"]: soil_type,
        schema_map["rainfall_mm"]: rainfall_mm,
        schema_map["temperature_c"]: temperature_c,
        schema_map["humidity_pct"]: humidity_pct,
    }
    if location:
        record["location"] = location
    return record


def load_selected_dataset(selected_dataset):
    if selected_dataset is None:
        return None, "unknown", {}
    dataframe = pd.read_csv(selected_dataset)
    schema_kind, schema_map = detect_schema(dataframe.columns)
    return dataframe, schema_kind, schema_map


inject_styles()

st.markdown(
    """
    <div class="hero-card">
        <div class="eyebrow">AgriVision AI</div>
        <h1>Crop Recommendation Dashboard</h1>
        <p>Choose a dataset, enter field conditions, compare scenarios, and review model results in one place.</p>
        <div class="hero-tags">
            <span class="hero-tag">Crop suggestions</span>
            <span class="hero-tag">Dataset insights</span>
            <span class="hero-tag">Scenario comparison</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

datasets = list_datasets()
selected_dataset = st.selectbox(
    "Active dataset",
    datasets,
    format_func=lambda path: path.name,
    index=0 if datasets else None,
    placeholder="Upload a CSV to begin" if not datasets else None,
)

dataset_df, schema_kind, schema_map = load_selected_dataset(selected_dataset) if selected_dataset else (None, "unknown", {})

tab_recommend, tab_upload, tab_fertilizer, tab_mandi, tab_evaluate, tab_compare = st.tabs(
    ["Recommend Crop", "Upload Training Dataset", "Fertilizer", "Mandi Prices", "Model Evaluation", "Compare Scenarios"]
)


with tab_recommend:
    if dataset_df is None:
        st.warning("📁 No datasets found in the dataset/ folder. Upload one in the **Upload Training Dataset** tab.")
    else:
        st.markdown("<div class='section-heading'>🌾 Get Crop Recommendation</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='section-subtitle'>Using dataset: <strong>{html.escape(selected_dataset.name)}</strong></div>", unsafe_allow_html=True)
        
        if schema_kind == "numeric":
            numeric_defaults = {}
            for logical_name, column_name in {"N": schema_map["n"], "P": schema_map["p"], "K": schema_map["k"], "temperature": schema_map["temperature"], "humidity": schema_map["humidity"], "ph": schema_map["ph"], "rainfall": schema_map["rainfall"]}.items():
                series = pd.to_numeric(dataset_df[column_name], errors="coerce")
                if series.notna().any():
                    numeric_defaults[logical_name] = float(series.median())

            record = render_numeric_input_panel("recommendation", schema_map, numeric_defaults)
            if st.button("🔍 Recommend crop", key="recommend_kaggle", use_container_width=True):
                result = backend_or_local_prediction(record)
                display_recommendation(result)
        elif schema_kind == "soil":
            soil_defaults = {}
            if schema_map["soil_type"] in dataset_df.columns and not dataset_df[schema_map["soil_type"]].dropna().empty:
                soil_defaults["soil_type"] = str(dataset_df[schema_map["soil_type"]].dropna().mode().iloc[0])
            for logical_name, column_name in {"rainfall_mm": schema_map["rainfall_mm"], "temperature_c": schema_map["temperature_c"], "humidity_pct": schema_map["humidity_pct"]}.items():
                series = pd.to_numeric(dataset_df[column_name], errors="coerce")
                if series.notna().any():
                    soil_defaults[logical_name] = float(series.median())

            record = render_soil_input_panel("recommendation", schema_map, soil_defaults)
            if st.button("🔍 Recommend crop", key="recommend_soil", use_container_width=True):
                result = recommend_from_record(record)
                display_recommendation(result)
        else:
            st.warning("Unrecognized dataset schema. Upload a supported dataset (soil-based or Kaggle-style).")

        with st.expander("📋 Dataset Preview & Statistics"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("<div class='section-heading'>Preview</div>", unsafe_allow_html=True)
                st.dataframe(dataset_df.head(), use_container_width=True)
            with col2:
                st.markdown("<div class='section-heading'>Schema</div>", unsafe_allow_html=True)
                st.write(f"Type: **{schema_kind}**")
                st.write(f"Rows: **{len(dataset_df)}**")
                st.write(f"Columns: **{len(dataset_df.columns)}**")
            
            render_dataset_analysis(dataset_df)


with tab_upload:
    st.markdown("<div class='section-heading'>📚 Upload & Train Models</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Upload CSV datasets and train recommendation models.</div>", unsafe_allow_html=True)
    
    st.markdown("**Supported formats:**")
    st.markdown("- **Soil-based**: `soil_type, rainfall_mm, temperature_c, humidity_pct, crop`")
    st.markdown("- **Kaggle-style**: `N, P, K, temperature, humidity, ph, rainfall, label`")

    uploaded_file = st.file_uploader("Upload training dataset (CSV)", type=["csv"], key="upload_file")
    if uploaded_file is not None:
        uploaded_file.seek(0)
        df_up = pd.read_csv(uploaded_file)
        st.markdown("<div class='section-heading'>Preview</div>", unsafe_allow_html=True)
        st.dataframe(df_up.head(), use_container_width=True)

        if st.button("✅ Save to dataset folder", key="save_dataset", use_container_width=True):
            dest = DATASET_DIR / uploaded_file.name
            with open(dest, "wb") as file_handle:
                file_handle.write(uploaded_file.getbuffer())
            st.success(f"✓ Saved to {dest.name}")
            st.info(f"To train: `python ml_model/train.py --dataset {dest.name}`")
            st.rerun()

    with st.expander("📂 Available datasets"):
        datasets_list = list_datasets()
        if datasets_list:
            for dataset_path in datasets_list:
                st.write(f"• **{dataset_path.name}** ({dataset_path.stat().st_size:,} bytes)")
        else:
            st.info("No datasets available yet.")

    st.markdown("---")
    st.markdown("<div class='section-heading'>Train Model</div>", unsafe_allow_html=True)
    available_datasets = list_datasets()
    if available_datasets:
        to_train = st.selectbox("Select dataset to train on", available_datasets, format_func=lambda path: path.name)
        if st.button("🚀 Train model on selected dataset", key="train_model", use_container_width=True):
            import subprocess
            st.info(f"Training on: {to_train.name}")
            try:
                command = [sys.executable, "ml_model/train.py", "--dataset", str(to_train)]
                process = subprocess.run(command, capture_output=True, text=True, check=False)
                if process.returncode == 0:
                    st.success("✓ Training completed successfully!")
                else:
                    st.error(f"Training failed with code {process.returncode}")
                    st.code(process.stdout + "\n" + process.stderr)
            except Exception as exc:
                st.error(f"Error: {exc}")
    else:
        st.info("Upload a dataset first to train a model.")


with tab_fertilizer:
    st.markdown("<div class='section-heading'>🌱 Fertilizer Recommendations</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Get fertilizer suggestions based on crop type and soil conditions.</div>", unsafe_allow_html=True)

    external_path = Path("d:/fertilizer_recommendation.csv")
    local_path = DATASET_DIR / "fertilizer_recommendation.csv"

    if external_path.exists() and not local_path.exists():
        if st.button("📥 Import fertilizer_recommendation.csv", use_container_width=True):
            import shutil
            shutil.copy(external_path, local_path)
            st.success(f"Imported to {local_path}")
            st.rerun()

    if local_path.exists():
        df_fert = pd.read_csv(local_path)
        
        with st.expander("📋 Dataset Preview", expanded=False):
            st.dataframe(df_fert.head(), use_container_width=True)

        st.markdown("<div class='section-heading'>Get Fertilizer Suggestion</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            crop_opts = sorted(df_fert["Crop_Type"].dropna().unique())
            chosen_crop = st.selectbox("Crop Type", crop_opts)
        with col2:
            soil_opts = sorted(df_fert["Soil_Type"].dropna().unique())
            chosen_soil = st.selectbox("Soil Type", soil_opts)

        cols = st.columns(3)
        nit = cols[0].number_input("Nitrogen (N)", min_value=0, max_value=100, value=50)
        phos = cols[1].number_input("Phosphorus (P)", min_value=0, max_value=100, value=40)
        pot = cols[2].number_input("Potassium (K)", min_value=0, max_value=100, value=60)

        if st.button("💡 Get suggestion", key="fert_suggest", use_container_width=True):
            try:
                response = requests.post(
                    "http://localhost:8000/fertilizer",
                    json={"crop": chosen_crop, "soil_type": chosen_soil, "N": nit, "P": phos, "K": pot},
                    timeout=5,
                )
                if response.status_code == 200:
                    fert_data = response.json()
                    st.success(f"**Recommended**: {fert_data.get('fertilizer', 'Unknown')}")
            except requests.exceptions.RequestException:
                st.warning("Backend unavailable. Using local data...")
                
        subset = df_fert[(df_fert["Crop_Type"] == chosen_crop) & (df_fert["Soil_Type"] == chosen_soil)]
        if not subset.empty:
            mode = subset["Recommended_Fertilizer"].mode()
            if not mode.empty:
                st.info(f"**Common fertilizer**: {mode.iloc[0]}")
    else:
        st.warning("📁 No fertilizer dataset found. Import or upload one.")


with tab_mandi:
    st.markdown("<div class='section-heading'>💰 Mandi / Market Prices</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Track commodity prices and market trends.</div>", unsafe_allow_html=True)

    external_mandi = Path("d:/mandi price/commodity_price.csv")
    local_mandi = DATASET_DIR / "commodity_price.csv"

    if external_mandi.exists() and not local_mandi.exists():
        if st.button("📥 Import external mandi CSV", use_container_width=True):
            import shutil
            shutil.copy(external_mandi, local_mandi)
            st.success(f"Imported to {local_mandi}")
            st.rerun()

    if local_mandi.exists():
        df_m = pd.read_csv(local_mandi)
        
        with st.expander("📋 Dataset Preview", expanded=False):
            st.dataframe(df_m.head(), use_container_width=True)

        commodity_cols = [c for c in df_m.columns if "commodity" in c.lower() or "crop" in c.lower()]
        price_cols = [c for c in df_m.columns if "price" in c.lower() or "rate" in c.lower() or df_m[c].dtype.kind in "fi"]

        if commodity_cols:
            commodity_col = commodity_cols[0]
            selected_commodity = st.selectbox("Select Commodity", sorted(df_m[commodity_col].dropna().unique()))
            filtered = df_m[df_m[commodity_col] == selected_commodity]
            st.write(f"Records: **{len(filtered)}**")
            
            if price_cols:
                price_col = price_cols[0]
                st.line_chart(filtered[price_col].reset_index(drop=True))
        else:
            st.info("No commodity column detected.")
            st.dataframe(df_m.describe(include='all'), use_container_width=True)
    else:
        st.warning("📁 No mandi dataset found. Import or upload one.")


with tab_evaluate:
    st.markdown("<div class='section-heading'>📊 Model Evaluation</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>View AI model performance metrics and accuracy.</div>", unsafe_allow_html=True)

    if REPORT_PATH.exists():
        report_text = REPORT_PATH.read_text(encoding="utf-8")
        with st.expander("📄 Evaluation Report", expanded=True):
            st.text(report_text)
    else:
        st.info("ℹ️ No evaluation report found yet.")

    if st.button("🔄 Run Model Evaluation", key="run_evaluation", use_container_width=True):
        with st.spinner("Evaluating model..."):
            try:
                report_text, metrics = evaluate_model()
                REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
                REPORT_PATH.write_text(report_text, encoding="utf-8")
                st.success("✓ Evaluation complete!")
                st.text(report_text)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Accuracy", f"{metrics['accuracy']:.1%}")
                with col2:
                    st.metric("Status", "✓ Complete")

                matrix = metrics["confusion_matrix"]
                labels = metrics["labels"]
                cm_df = pd.DataFrame(matrix, index=labels, columns=labels)
                st.markdown("<div class='section-heading'>Confusion Matrix</div>", unsafe_allow_html=True)
                st.dataframe(cm_df, use_container_width=True)
            except Exception as exc:
                st.error(f"❌ Evaluation failed: {exc}")
                st.info("Ensure the model is trained and dataset exists.")


with tab_compare:
    st.markdown("<div class='section-heading'>⚖️ Compare Scenarios</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Compare crop recommendations for two different conditions side-by-side.</div>", unsafe_allow_html=True)

    if dataset_df is None:
        st.warning("📁 No dataset selected. Upload one first.")
    elif schema_kind not in {"numeric", "soil"}:
        st.warning("Schema not supported for comparison.")
    else:
        left_col, right_col = st.columns(2)

        defaults_left = {}
        defaults_right = {}
        if schema_kind == "numeric":
            for logical_name, column_name in {"N": schema_map["n"], "P": schema_map["p"], "K": schema_map["k"], "temperature": schema_map["temperature"], "humidity": schema_map["humidity"], "ph": schema_map["ph"], "rainfall": schema_map["rainfall"]}.items():
                series = pd.to_numeric(dataset_df[column_name], errors="coerce")
                if series.notna().any():
                    defaults_left[logical_name] = float(series.median())
                    defaults_right[logical_name] = float(series.median())
        else:
            if schema_map["soil_type"] in dataset_df.columns and not dataset_df[schema_map["soil_type"]].dropna().empty:
                dominant_soil = str(dataset_df[schema_map["soil_type"]].dropna().mode().iloc[0])
                defaults_left["soil_type"] = dominant_soil
                defaults_right["soil_type"] = dominant_soil
            for logical_name, column_name in {"rainfall_mm": schema_map["rainfall_mm"], "temperature_c": schema_map["temperature_c"], "humidity_pct": schema_map["humidity_pct"]}.items():
                series = pd.to_numeric(dataset_df[column_name], errors="coerce")
                if series.notna().any():
                    defaults_left[logical_name] = float(series.median())
                    defaults_right[logical_name] = float(series.median())

        with left_col:
            st.markdown("<div class='panel-card'><div class='eyebrow'>Scenario A</div></div>", unsafe_allow_html=True)
            record_a = render_numeric_input_panel("scenario_a", schema_map, defaults_left) if schema_kind == "numeric" else render_soil_input_panel("scenario_a", schema_map, defaults_left)
        
        with right_col:
            st.markdown("<div class='panel-card'><div class='eyebrow'>Scenario B</div></div>", unsafe_allow_html=True)
            record_b = render_numeric_input_panel("scenario_b", schema_map, defaults_right) if schema_kind == "numeric" else render_soil_input_panel("scenario_b", schema_map, defaults_right)

        if st.button("⚖️ Compare scenarios", key="compare_scenarios", use_container_width=True):
            result_a = backend_or_local_prediction(record_a, show_feedback=False) if schema_kind == "numeric" else recommend_from_record(record_a)
            result_b = backend_or_local_prediction(record_b, show_feedback=False) if schema_kind == "numeric" else recommend_from_record(record_b)

            out_left, out_right = st.columns(2)
            with out_left:
                display_recommendation(result_a, title="Scenario A")
            with out_right:
                display_recommendation(result_b, title="Scenario B")
