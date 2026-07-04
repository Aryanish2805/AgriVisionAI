# ============================================================
# AI BASED AGRICULTURE RECOMMENDATION SYSTEM
# Streamlit Application
# ============================================================

import streamlit as st
import pandas as pd
import joblib


# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="AI Agriculture System",
    page_icon="🌱",
    layout="wide"
)


# ============================================================
# LOAD ML MODELS
# ============================================================

@st.cache_resource
def load_models():

    try:

        crop_model = joblib.load("models/crop_model.pkl")

        fertilizer_model = joblib.load(
            "models/fertilizer_model.pkl"
        )

        price_model = joblib.load(
            "models/price_model.pkl"
        )

        crop_encoder = joblib.load(
            "models/crop_label_encoder.pkl"
        )

        crop_scaler = joblib.load(
            "models/crop_scaler.pkl"
        )

        fertilizer_encoder = joblib.load(
            "models/fertilizer_label_encoder.pkl"
        )

        return (
            crop_model,
            fertilizer_model,
            price_model,
            crop_encoder,
            fertilizer_encoder,
            crop_scaler
        )

    except Exception as error:

        st.error(
            "Model loading failed"
        )

        st.exception(
            error
        )

        return None



models = load_models()


if models is None:

    st.stop()


(
    crop_model,
    fertilizer_model,
    price_model,
    crop_encoder,
    fertilizer_encoder,
    crop_scaler

) = models



# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🌱 Smart Agriculture AI"
)


page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "🌾 Crop Recommendation",
        "🧪 Fertilizer Recommendation",
        "💰 Price Prediction"
    ]
)



# ============================================================
# HOME PAGE
# ============================================================

# ============================================================
# HOME DASHBOARD
# ============================================================

if page == "🏠 Home":


    st.title(
        "🌱 AI-Based Smart Agriculture Recommendation System"
    )


    st.markdown(
        """
        ### Intelligent Farming Assistant using Machine Learning

        This system analyzes soil nutrients, environmental
        conditions and market information to provide
        data-driven agricultural recommendations.
        """
    )


    st.divider()


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            label="🌾 Crop Recommendation",
            value="Active"
        )


        st.write(
            "Predicts the most suitable crop using soil and climate parameters."
        )


    with col2:

        st.metric(
            label="🧪 Fertilizer Recommendation",
            value="Active"
        )


        st.write(
            "Suggests fertilizers using soil health and crop information."
        )


    with col3:

        st.metric(
            label="💰 Price Prediction",
            value="Active"
        )


        st.write(
            "Predicts expected crop market price using historical data."
        )


    st.divider()


    st.subheader(
        "Machine Learning Models"
    )


    m1, m2, m3 = st.columns(3)


    with m1:

        st.info(
            """
            Crop Model
            
            Algorithm:
            Extra Trees Classifier
            
            Accuracy:
            99%+
            """
        )


    with m2:

        st.info(
            """
            Fertilizer Model
            
            Ensemble Learning
            
            Accuracy:
            88%+
            """
        )


    with m3:

        st.info(
            """
            Price Model
            
            Regression Model
            
            R² Score:
            0.84+
            """
        )


    st.success(
        "All AI models loaded and ready for prediction"
    )

# ============================================================
# CROP RECOMMENDATION PAGE
# ============================================================

elif page == "🌾 Crop Recommendation":


    st.title(
        "🌾 Crop Recommendation System"
    )


    st.write(
        "Enter soil and environmental parameters"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        nitrogen = st.number_input(
            "Nitrogen (N)",
            min_value=0
        )

        phosphorus = st.number_input(
            "Phosphorus (P)",
            min_value=0
        )

        potassium = st.number_input(
            "Potassium (K)",
            min_value=0
        )


    with col2:

        temperature = st.number_input(
            "Temperature (°C)"
        )

        humidity = st.number_input(
            "Humidity (%)"
        )


    with col3:

        ph = st.number_input(
            "Soil pH"
        )

        rainfall = st.number_input(
            "Rainfall (mm)"
        )



    if st.button(
        "Recommend Crop"
    ):


        npk_total = (
            nitrogen
            + phosphorus
            + potassium
        )


        if npk_total == 0:

            st.warning(
                "NPK values cannot all be zero"
            )


        else:


            crop_values = {

                "nitrogen": nitrogen,

                "phosphorus": phosphorus,

                "potassium": potassium,

                "temperature": temperature,

                "humidity": humidity,

                "ph": ph,

                "rainfall": rainfall,

                "npk_total": npk_total,

                "nitrogen_ratio":
                    nitrogen / npk_total,

                "phosphorus_ratio":
                    phosphorus / npk_total,

                "potassium_ratio":
                    potassium / npk_total

            }



            if ph < 6.5:

                crop_values[
                    "soil_condition"
                ] = "acidic"


            elif ph <= 7.5:

                crop_values[
                    "soil_condition"
                ] = "neutral"


            else:

                crop_values[
                    "soil_condition"
                ] = "alkaline"

            scaled_values = crop_scaler.transform(
                [[
                    nitrogen,
                    phosphorus,
                    potassium,
                    temperature,
                    humidity,
                    ph,
                    rainfall
                ]]
            )

            crop_values["nitrogen_scaled"] = scaled_values[0][0]
            crop_values["phosphorus_scaled"] = scaled_values[0][1]
            crop_values["potassium_scaled"] = scaled_values[0][2]
            crop_values["temperature_scaled"] = scaled_values[0][3]
            crop_values["humidity_scaled"] = scaled_values[0][4]
            crop_values["ph_scaled"] = scaled_values[0][5]
            crop_values["rainfall_scaled"] = scaled_values[0][6]

            crop_input = pd.DataFrame(
                [crop_values]
            )


            crop_input = crop_input.reindex(
                columns=crop_model.feature_names_in_,
                fill_value=0
            )


            prediction = crop_model.predict(
                crop_input
            )


            crop_name = (
                crop_encoder
                .inverse_transform(
                    prediction
                )[0]
            )


            st.success(
                f"🌱 Recommended Crop: {crop_name}"
            )



# ============================================================
# FERTILIZER PAGE
# ============================================================

# ============================================================
# FERTILIZER RECOMMENDATION PAGE
# ============================================================

elif page == "🧪 Fertilizer Recommendation":


    st.title(
        "🧪 Fertilizer Recommendation System"
    )


    st.write(
        "Enter soil, crop and environmental details"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        soil_ph = st.number_input(
            "Soil pH",
            value=6.5
        )

        soil_moisture = st.number_input(
            "Soil Moisture",
            value=40.0
        )

        organic_carbon = st.number_input(
            "Organic Carbon",
            value=0.5
        )

        electrical_conductivity = st.number_input(
            "Electrical Conductivity",
            value=0.5
        )


    with col2:

        nitrogen_level = st.number_input(
            "Nitrogen Level",
            value=50
        )

        phosphorus_level = st.number_input(
            "Phosphorus Level",
            value=40
        )

        potassium_level = st.number_input(
            "Potassium Level",
            value=40
        )

        yield_last_season = st.number_input(
            "Last Season Yield",
            value=1000
        )


    with col3:

        temperature = st.number_input(
            "Temperature",
            value=25
        )

        humidity = st.number_input(
            "Humidity",
            value=70
        )

        rainfall = st.number_input(
            "Rainfall",
            value=100
        )

        fertilizer_used = st.number_input(
            "Last Season Fertilizer",
            value=0
        )



    soil_type = st.selectbox(
        "Soil Type",
        [
            "clay",
            "loamy",
            "sandy",
            "silt"
        ]
    )


    crop_type = st.selectbox(
        "Crop Type",
        [
            "rice",
            "wheat",
            "maize",
            "cotton",
            "potato",
            "tomato",
            "sugarcane"
        ]
    )


    season = st.selectbox(
        "Season",
        [
            "kharif",
            "rabi",
            "zaid"
        ]
    )



    if st.button(
        "Recommend Fertilizer"
    ):


        fertilizer_input = pd.DataFrame(
            [[0] * len(
                fertilizer_model.feature_names_in_
            )],
            columns=fertilizer_model.feature_names_in_
        )



        values = {

            "soil_ph": soil_ph,

            "soil_moisture": soil_moisture,

            "organic_carbon": organic_carbon,

            "electrical_conductivity":
                electrical_conductivity,

            "nitrogen_level":
                nitrogen_level,

            "phosphorus_level":
                phosphorus_level,

            "potassium_level":
                potassium_level,

            "temperature":
                temperature,

            "humidity":
                humidity,

            "rainfall":
                rainfall,

            "fertilizer_used_last_season":
                fertilizer_used,

            "yield_last_season":
                yield_last_season

        }



        for column in values:

            if column in fertilizer_input.columns:

                fertilizer_input[column] = values[column]



        fertilizer_input[
            "soil_type_" + soil_type
        ] = 1


        fertilizer_input[
            "crop_type_" + crop_type
        ] = 1


        fertilizer_input[
            "season_" + season
        ] = 1



        prediction = fertilizer_model.predict(
            fertilizer_input
        )


        fertilizer_name = (
            fertilizer_encoder
            .inverse_transform(
                prediction
            )[0]
        )


        st.success(
            f"🧪 Recommended Fertilizer: {fertilizer_name}"
        )


# ============================================================
# PRICE PAGE
# ============================================================

# ============================================================
# PRICE PREDICTION PAGE
# ============================================================

elif page == "💰 Price Prediction":


    st.title(
        "💰 Crop Market Price Prediction"
    )


    st.write(
        "Enter market and crop details"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        year = st.number_input(
            "Year",
            value=2026
        )


        month = st.number_input(
            "Month",
            min_value=1,
            max_value=12,
            value=7
        )


        state_code = st.number_input(
            "State Code",
            value=1
        )


    with col2:

        district_code = st.number_input(
            "District Code",
            value=1
        )


        market_code = st.number_input(
            "Market Code",
            value=1
        )


        commodity_code = st.number_input(
            "Commodity Code",
            value=1
        )


    with col3:

        variety_code = st.number_input(
            "Variety Code",
            value=1
        )


        grade_code = st.number_input(
            "Grade Code",
            value=1
        )


        price_difference = st.number_input(
            "Price Difference",
            value=0
        )



    if st.button(
        "Predict Price"
    ):


        price_input = pd.DataFrame(
            [
                {

                    "year": year,

                    "month": month,

                    "state_code": state_code,

                    "district_code": district_code,

                    "market_code": market_code,

                    "commodity_code": commodity_code,

                    "variety_code": variety_code,

                    "grade_code": grade_code,

                    "price_difference": price_difference

                }
            ]
        )


        price_input = price_input.reindex(
            columns=price_model.feature_names_in_
        )


        predicted_price = price_model.predict(
            price_input
        )[0]


        st.success(
            f"💰 Predicted Market Price: ₹{predicted_price:.2f}"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    ### 🌱 Smart Agriculture AI System

    **Features**
    - Crop Recommendation using Machine Learning
    - Fertilizer Recommendation using AI Models
    - Crop Market Price Prediction

    **Technology Stack**
    - Python
    - Streamlit
    - Machine Learning
    - Scikit-Learn

    Developed as an AI-Based Agriculture Recommendation Project
    """
)