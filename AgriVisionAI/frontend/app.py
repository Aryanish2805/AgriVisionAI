import streamlit as st
import sys
import requests
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from ml_model.crop_recommender import recommend_from_record
from ml_model.evaluate import evaluate_model

DATASET_DIR = Path(__file__).resolve().parents[1] / "dataset"
REPORT_PATH = Path(__file__).resolve().parents[1] / "reports" / "model_evaluation.txt"

st.set_page_config(page_title="AI-Based Crop Recommendation System")

st.title("🌾 AI-Based Crop Recommendation System")
st.markdown("Use the tabs to recommend the best crop, upload training data, or view model evaluation metrics.")

tab_recommend, tab_upload, tab_fertilizer, tab_mandi, tab_evaluate = st.tabs(["Recommend Crop", "Upload Training Dataset", "Fertilizer", "Mandi Prices", "Model Evaluation"])

def list_datasets():
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    return sorted([p for p in DATASET_DIR.glob("*.csv")])


def display_recommendation(result):
    if not result or not result.get("suggestions"):
        st.info(result.get("message", "No suggestion available"))
        return

    top_crop, top_prob = result["suggestions"][0]
    if top_prob is not None:
        st.success(f"Recommended crop: {top_crop} ({top_prob:.2%})")
    else:
        st.success(f"Recommended crop: {top_crop}")

    if len(result["suggestions"]) > 1:
        rows = []
        for name, prob in result["suggestions"]:
            rows.append({"Crop": name, "Probability": f"{prob:.2%}" if prob is not None else "N/A"})
        st.markdown("### Other candidate crops")
        st.dataframe(rows)


# simple location -> soil presets (expandable)
LOCATION_SOIL_PRESETS = {
    "karnataka": "Loamy",
    "punjab": "Loamy",
    "uttar pradesh": "Silty",
    "maharashtra": "Sandy",
}


with tab_recommend:
    datasets = list_datasets()
    if not datasets:
        st.warning("No datasets found in the dataset/ folder. Upload one in the Upload tab.")
    else:
        selected = st.selectbox("Select dataset", datasets, format_func=lambda p: p.name)
        import pandas as pd

        df = pd.read_csv(selected)
        cols = {c.strip().lower(): c for c in df.columns}

        st.write(f"Using dataset: {selected.name}")
        st.write("Preview:")
        st.dataframe(df.head())

        # Render form based on detected schema
        if "soil_type" in cols:
            soil_col = cols["soil_type"]
            rain_col = cols.get("rainfall_mm", "rainfall_mm")
            temp_col = cols.get("temperature_c", "temperature_c")
            hum_col = cols.get("humidity_pct", "humidity_pct")

            soils_list = ["Loamy", "Sandy", "Clay", "Silty", "Peaty", "Chalky"]
            # allow user to enter location to auto-suggest soil
            location = st.text_input("Location (optional)", value="")
            suggested_soil = None
            if location:
                suggested_soil = LOCATION_SOIL_PRESETS.get(location.strip().lower())
            default_index = soils_list.index(suggested_soil) if suggested_soil in soils_list else 0
            soil_type = st.selectbox("Soil type", soils_list, index=default_index)
            rainfall_mm = st.number_input("Estimated rainfall (mm)", min_value=0.0, max_value=500.0, value=120.0)
            temperature_c = st.number_input("Average temperature (°C)", min_value=-10.0, max_value=50.0, value=25.0)
            humidity_pct = st.number_input("Relative humidity (%)", min_value=0.0, max_value=100.0, value=60.0)

            record = {soil_col: soil_type, rain_col: rainfall_mm, temp_col: temperature_c, hum_col: humidity_pct}
            if location:
                record["location"] = location

            if st.button("Recommend crop", key="recommend_soil"):
                result = recommend_from_record(record)
                display_recommendation(result)

        elif {"n", "p", "k", "temperature", "humidity", "ph", "rainfall"}.issubset(set(cols.keys())):
            # Kaggle-style numeric schema
            col_N = cols["n"]
            col_P = cols["p"]
            col_K = cols["k"]
            col_temp = cols["temperature"]
            col_hum = cols["humidity"]
            col_ph = cols["ph"]
            col_rain = cols["rainfall"]

            N = st.number_input("Nitrogen (N)", min_value=0.0, value=50.0)
            P = st.number_input("Phosphorus (P)", min_value=0.0, value=50.0)
            K = st.number_input("Potassium (K)", min_value=0.0, value=50.0)
            temperature = st.number_input("Temperature (°C)", value=25.0)
            humidity = st.number_input("Humidity (%)", value=70.0)
            ph = st.number_input("Soil pH", value=6.5)
            rainfall = st.number_input("Rainfall", value=100.0)

            location = st.text_input("Location (optional)", value="")

            record = {
                col_N: N,
                col_P: P,
                col_K: K,
                col_temp: temperature,
                col_hum: humidity,
                col_ph: ph,
                col_rain: rainfall,
            }
            if location:
                record["location"] = location

            if st.button("Recommend crop", key="recommend_kaggle"):
                try:
                    # Make HTTP POST to FastAPI backend
                    response = requests.post(
                        "http://localhost:8000/predict",
                        json=record,
                        timeout=5
                    )
                    if response.status_code == 200:
                        backend_data = response.json()
                        # Format it to match what display_recommendation expects
                        if backend_data.get("candidates"):
                            suggestions = [(c["crop"], c["probability"]) for c in backend_data["candidates"]]
                        else:
                            suggestions = [(backend_data.get("recommended_crop", "Unknown"), None)]
                        
                        result = {
                            "type": "ml",
                            "suggestions": suggestions,
                            "message": "Prediction from Backend API"
                        }
                    else:
                        st.error(f"Backend API Error: {response.text}")
                        result = recommend_from_record(record)
                except requests.exceptions.RequestException:
                    st.warning("Backend API is unreachable. Falling back to local model.")
                    result = recommend_from_record(record)
                
                display_recommendation(result)

        else:
            st.warning("Unrecognized dataset schema. Upload a supported dataset (soil-based or Kaggle-style).")

        st.markdown("### How recommendations work")
        st.write(
            "This app first tries to use a trained ML model from `ml_model/crop_model.joblib`. "
            "If the model is available, it returns the best crop plus candidate probabilities. "
            "If no model is present or the input schema does not match, it falls back to a rule-based recommendation using soil, rainfall, and temperature."
        )
        st.info("Click 'Recommend crop' after entering all inputs.")
        st.info("If a trained ML model exists in `ml_model/crop_model.joblib`, the app will use it automatically; otherwise it will fall back to rule-based crop recommendation.")
        st.info("To train a model from a CSV file, run: python ml_model/train.py --dataset dataset/yourfile.csv")

    with tab_upload:
        st.write("Upload a crop recommendation CSV dataset. The app supports two common schemas:")
        st.markdown("- Soil-based: `soil_type, rainfall_mm, temperature_c, humidity_pct, crop`\n- Kaggle-style: `N,P,K,temperature,humidity,ph,rainfall,label`")

        uploaded_file = st.file_uploader("Upload training dataset (CSV)", type=["csv"], key="upload_file")
        if uploaded_file is not None:
            import pandas as pd

            uploaded_file.seek(0)
            df_up = pd.read_csv(uploaded_file)
            st.write("Uploaded dataset preview:")
            st.dataframe(df_up.head())

            if st.button("Save to dataset folder", key="save_dataset"):
                dest = DATASET_DIR / uploaded_file.name
                with open(dest, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Saved training dataset to {dest}")
                st.info(f"Then run: python ml_model/train.py --dataset {dest}")
                st.write("After saving, you can train the model with the dataset above or by using the button below.")

        # show current files
        st.write("Available datasets in dataset/:")
        for p in list_datasets():
            st.write(f"- {p.name} ({p.stat().st_size} bytes)")

        # Training controls
        st.markdown("---")
        st.subheader("Train model")
        datasets = list_datasets()
        if datasets:
            to_train = st.selectbox("Select dataset to train on", datasets, format_func=lambda p: p.name)
            if st.button("Train model on selected dataset", key="train_model"):
                import subprocess

                st.info(f"Training model on: {to_train.name}")
                try:
                    cmd = [sys.executable, "ml_model/train.py", "--dataset", str(to_train)]
                    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
                    st.code(proc.stdout + "\n" + proc.stderr)
                    if proc.returncode == 0:
                        st.success("Training completed successfully.")
                    else:
                        st.error(f"Training exited with code {proc.returncode}")
                except Exception as e:
                    st.error(f"Training failed: {e}")
        else:
            st.info("No datasets available to train.")


with tab_fertilizer:
    st.title("Fertilizer Recommendations")
    st.write("Upload or import a fertilizer recommendation CSV and get simple suggestions based on nearest records.")

    # possible source paths
    external_path = Path("d:/fertilizer_recommendation.csv")
    local_path = DATASET_DIR / "fertilizer_recommendation.csv"

    if external_path.exists() and not local_path.exists():
        if st.button("Import fertilizer_recommendation.csv into project dataset"):
            import shutil

            shutil.copy(external_path, local_path)
            st.success(f"Imported to {local_path}")

    if local_path.exists():
        import pandas as pd

        df_fert = pd.read_csv(local_path)
        st.subheader("Fertilizer dataset preview")
        st.dataframe(df_fert.head())

        st.write("Simple lookup: choose crop and soil to get common recommendations")
        crop_opts = sorted(df_fert["Crop_Type"].dropna().unique())
        soil_opts = sorted(df_fert["Soil_Type"].dropna().unique())
        chosen_crop = st.selectbox("Crop", crop_opts)
        chosen_soil = st.selectbox("Soil Type", soil_opts)

        nit = st.number_input("Nitrogen level (N)", value=50)
        phos = st.number_input("Phosphorus level (P)", value=40)
        pot = st.number_input("Potassium level (K)", value=60)

        if st.button("Get fertilizer suggestion"):
            try:
                response = requests.post(
                    "http://localhost:8000/fertilizer",
                    json={"crop": chosen_crop, "soil_type": chosen_soil, "N": nit, "P": phos, "K": pot},
                    timeout=5
                )
                if response.status_code == 200:
                    fert_data = response.json()
                    st.success(f"Backend Recommended Fertilizer: {fert_data.get('fertilizer', 'Unknown')}")
                    if fert_data.get('details'):
                        st.info(fert_data['details'].get('message', ''))
                else:
                    st.error("Backend Error. Falling back to local data.")
                    raise requests.exceptions.RequestException()
            except requests.exceptions.RequestException:
                sub = df_fert[(df_fert["Crop_Type"] == chosen_crop) & (df_fert["Soil_Type"] == chosen_soil)]
                if not sub.empty:
                    mode = sub["Recommended_Fertilizer"].mode()
                    if not mode.empty:
                        st.success(f"Common recommended fertilizer for selected crop/soil: {mode.iloc[0]}")
                    else:
                        st.info("No clear mode; showing nearest records")
                        sub = df_fert
                else:
                    st.info("No exact match found; using nearest records by N,P,K")
                    sub = df_fert

            # compute simple distance on N,P,K
            numeric_cols = ["Nitrogen_Level", "Phosphorus_Level", "Potassium_Level"]
            sub = sub.dropna(subset=numeric_cols + ["Recommended_Fertilizer"]).copy()
            if not sub.empty:
                sub["dist"] = ((sub["Nitrogen_Level"] - nit) ** 2 + (sub["Phosphorus_Level"] - phos) ** 2 + (sub["Potassium_Level"] - pot) ** 2) ** 0.5
                nearest = sub.nsmallest(5, "dist")[ ["Crop_Type","Soil_Type","Nitrogen_Level","Phosphorus_Level","Potassium_Level","Recommended_Fertilizer","dist"] ]
                st.subheader("Nearest historical matches")
                st.dataframe(nearest)
    else:
        st.warning("No fertilizer dataset found. Upload or import one from d:/fertilizer_recommendation.csv")


with tab_mandi:
    st.title("Mandi / Market Prices")
    st.write("Preview commodity price CSV and basic summaries. You can import an external file into the project dataset.")

    external_mandi = Path("d:/mandi price/commodity_price.csv")
    local_mandi = DATASET_DIR / "commodity_price.csv"

    if external_mandi.exists() and not local_mandi.exists():
        if st.button("Import external mandi CSV into project dataset"):
            import shutil

            shutil.copy(external_mandi, local_mandi)
            st.success(f"Imported to {local_mandi}")

    if local_mandi.exists():
        import pandas as pd

        df_m = pd.read_csv(local_mandi)
        st.subheader("Mandi dataset preview")
        st.dataframe(df_m.head())

        # if commodity column exists, allow selection
        commodity_cols = [c for c in df_m.columns if "commodity" in c.lower() or "crop" in c.lower()]
        price_cols = [c for c in df_m.columns if "price" in c.lower() or "rate" in c.lower() or df_m[c].dtype.kind in "fi"]

        if commodity_cols:
            commodity_col = commodity_cols[0]
            sel = st.selectbox("Commodity", sorted(df_m[commodity_col].dropna().unique()))
            filt = df_m[df_m[commodity_col] == sel]
            st.write(f"Rows for {sel}: {len(filt)}")
            if price_cols:
                pcol = price_cols[0]
                st.line_chart(filt[pcol].reset_index(drop=True))
        else:
            st.info("No commodity column detected; showing basic stats")
            st.write(df_m.describe(include='all'))

with tab_evaluate:
    st.write("View saved model evaluation metrics or refresh the evaluation report.")

    if REPORT_PATH.exists():
        report_text = REPORT_PATH.read_text(encoding="utf-8")
        st.subheader("Saved Evaluation Report")
        st.text(report_text)
    else:
        st.warning("No saved evaluation report found. Run evaluation to create one.")

    if st.button("Run Model Evaluation", key="run_evaluation"):
        try:
            report_text, metrics = evaluate_model()
            REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
            REPORT_PATH.write_text(report_text, encoding="utf-8")
            st.success("Evaluation complete and report saved.")
            st.text(report_text)

            st.subheader("Evaluation Metrics")
            st.metric("Accuracy", f"{metrics['accuracy']:.2%}")

            matrix = metrics["confusion_matrix"]
            labels = metrics["labels"]
            import pandas as pd

            cm_df = pd.DataFrame(matrix, index=labels, columns=labels)
            st.subheader("Confusion Matrix")
            st.dataframe(cm_df)
            st.bar_chart(cm_df)
        except Exception as exc:
            st.error(f"Evaluation failed: {exc}")
            st.info("Make sure the model is trained and the dataset CSV exists.")

