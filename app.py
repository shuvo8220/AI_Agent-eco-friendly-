import streamlit as st
import requests
import datetime
import tempfile
import os
import time
from gtts import gTTS
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import random
from datetime import datetime
import pydeck as pdk
import plotly.express as px

# ----------------------------
# CONFIGURATION
# ----------------------------
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"
WEATHER_API = "https://wttr.in/"


# SIDEBAR NAVIGATION
# ----------------------------
st.set_page_config(page_title="Eco Agent BD 🌿", layout="wide")
st.sidebar.title("🌿 Eco Agent BD")
page = st.sidebar.radio("Select a Page", [
    "🏙️ Weather",
    "🧮 Emission Calculator",
    "📊 Emission Breakdown",
    "🔍 Eco Search",
    "🤖 Eco AI Assistant",
    "✅ Tasks & Rewards"
])

EMISSION_FACTORS = {
    "Bangladesh": {
        "CNG": 0.055, "Bus": 0.028, "Uber": 0.14,
        "Electricity": 0.62, "Diet": 1.15, "Waste": 0.09
    }
}

CITIES = [
    "Dhaka", "Chittagong", "Khulna", "Rajshahi", "Sylhet",
    "Barisal", "Rangpur", "Mymensingh", "Comilla", "Narayanganj",
    "Gazipur", "Jessore", "Bogra", "Cox's Bazar", "Tangail",
    "Narsingdi", "Kushtia", "Feni", "Moulvibazar", "Pabna"
]


CITY_COORDS = {
    "Dhaka": (23.8103, 90.4125),
    "Chittagong": (22.3569, 91.7832),
    "Khulna": (22.8456, 89.5403),
    "Rajshahi": (24.3745, 88.6042),
    "Sylhet": (24.8949, 91.8687),
    "Barisal": (22.7010, 90.3535),
    "Rangpur": (25.7460, 89.2500),
    "Mymensingh": (24.7471, 90.4203),
    "Comilla": (23.4607, 91.1809),
    "Narayanganj": (23.6238, 90.5000),
    "Gazipur": (23.9999, 90.4203),
    "Jessore": (23.1706, 89.2140),
    "Bogra": (24.8481, 89.3730),
    "Cox's Bazar": (21.4272, 92.0058),
    "Tangail": (24.2513, 89.9167),
    "Narsingdi": (23.9323, 90.7152),
    "Kushtia": (23.9013, 89.1205),
    "Feni": (22.9415, 91.3958),
    "Moulvibazar": (24.4829, 91.7774),
    "Pabna": (24.0064, 89.2372)
}


# ----------------------------
# 1. WEATHER PAGE
# ----------------------------
if page == "🏙️ Weather":
    st.title("🌍 Carbon Emission Map + Weather Trend")

    selected_city = st.selectbox("Select a city for trend analysis:", CITIES)

    try:
        # ---- Current Weather ----
        res = requests.get(f"{WEATHER_API}{selected_city}?format=j1")
        data = res.json()
        curr = data["current_condition"][0]
        lat, lon = CITY_COORDS[selected_city]
        st.success(f"📍 {selected_city}: {curr['temp_C']}°C | {curr['weatherDesc'][0]['value']} | Humidity: {curr['humidity']}%")

        # ---- Historical Weather Trend ----
        weather_days = data["weather"]
        trend_data = []
        for day in weather_days:
            date = day["date"]
            avgtempC = float(day["avgtempC"])
            humidity = float(day["hourly"][4]["humidity"])  # midday

            trend_data.append({
                "Date": date,
                "Temperature": avgtempC,
                "Humidity": humidity
            })
        trend_df = pd.DataFrame(trend_data)

        st.subheader("📈 Historical Temperature Trend")
        fig_temp = px.line(trend_df, x="Date", y="Temperature", title=f"{selected_city} Temperature Trend")
        st.plotly_chart(fig_temp)

        st.subheader("💧 Historical Humidity Trend")
        fig_humid = px.line(trend_df, x="Date", y="Humidity", title=f"{selected_city} Humidity Trend")
        st.plotly_chart(fig_humid)

        # ---- Carbon Emission Map ----
        st.subheader("🗺️ Estimated Carbon Emission by City (Map View)")

        # Random simulated carbon emission (0-100 scale)
        carbon_data = []
        for city in CITIES:
            lat_, lon_ = CITY_COORDS[city]
            emission = random.randint(20, 100)  # Simulated value
            carbon_data.append({
                "City": city,
                "lat": lat_,
                "lon": lon_,
                "emission": emission
            })

        df_emission = pd.DataFrame(carbon_data)

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_emission,
            get_position='[lon, lat]',
            get_color='[emission * 2, 255 - emission * 2, 50, 160]',
            get_radius='emission * 100',
            pickable=True
        )

        view_state = pdk.ViewState(latitude=23.6850, longitude=90.3563, zoom=6.0)

        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{City}: {emission} CO₂ units"}
        ))

    except Exception as e:
        st.warning("⚠️ Weather data not available.")
        st.text(str(e))


# ----------------------------
# 2. CO₂ EMISSION CALCULATOR
# ----------------------------
# 2. CO₂ EMISSION CALCULATOR (ENHANCED)
# ----------------------------
elif page == "🧮 Emission Calculator":
    st.title("🧮 CO₂ Emission Calculator (Enhanced)")

    c1, c2 = st.columns(2)
    with c1:
        cng = st.slider("🚖 CNG (km/day)", 0.0, 100.0, 10.0)
        bus = st.slider("🚌 Bus (km/day)", 0.0, 100.0, 10.0)
        uber = st.slider("🚗 Uber (km/day)", 0.0, 50.0, 5.0)
        bike = st.slider("🚲 Bike (km/day)", 0.0, 50.0, 5.0)
        motorbike = st.slider("🏍️ Motorbike (km/day)", 0.0, 50.0, 5.0)
        air = st.slider("✈️ Air Travel (km/month)", 0.0, 3000.0, 0.0)
    with c2:
        elec = st.slider("🔌 Electricity (kWh/month)", 0.0, 1000.0, 200.0)
        lpg = st.slider("⛽ LPG (kg/month)", 0.0, 50.0, 5.0)
        water = st.slider("🚿 Water (liters/day)", 0.0, 500.0, 100.0)
        meals = st.number_input("🍱 Meals/day", 1, 10, 3)
        waste = st.slider("🗑️ Waste (kg/week)", 0.0, 50.0, 5.0)

    # Updated emission factors
    EF = {
        "CNG": 0.055, "Bus": 0.028, "Uber": 0.14,
        "Bike": 0.005, "Motorbike": 0.08, "Air": 0.25,
        "Electricity": 0.62, "LPG": 1.5, "Water": 0.0003,
        "Diet": 1.15, "Waste": 0.09
    }

    def calculate_emissions():
        daily = (
            EF["CNG"] * cng +
            EF["Bus"] * bus +
            EF["Uber"] * uber +
            EF["Bike"] * bike +
            EF["Motorbike"] * motorbike +
            EF["Water"] * water +
            EF["Diet"] * meals
        )
        monthly = (
            daily * 30 +
            EF["Electricity"] * elec +
            EF["LPG"] * lpg +
            EF["Air"] * air +
            EF["Waste"] * waste * 4
        )
        yearly = (
            daily * 365 +
            EF["Electricity"] * elec * 12 +
            EF["LPG"] * lpg * 12 +
            EF["Air"] * air * 12 +
            EF["Waste"] * waste * 52
        )
        breakdown = {
            "CNG": EF["CNG"] * cng * 30,
            "Bus": EF["Bus"] * bus * 30,
            "Uber": EF["Uber"] * uber * 30,
            "Bike": EF["Bike"] * bike * 30,
            "Motorbike": EF["Motorbike"] * motorbike * 30,
            "Electricity": EF["Electricity"] * elec,
            "LPG": EF["LPG"] * lpg,
            "Water": EF["Water"] * water * 30,
            "Air": EF["Air"] * air,
            "Diet": EF["Diet"] * meals * 30,
            "Waste": EF["Waste"] * waste * 4
        }
        return {
            "daily": round(daily / 1000, 3),
            "monthly": round(monthly / 1000, 3),
            "yearly": round(yearly / 1000, 3),
            "breakdown": {k: round(v / 1000, 3) for k, v in breakdown.items()}
        }

    if st.button("Calculate Emissions"):
        result = calculate_emissions()
        st.success(f"""
        📆 **Daily Emissions**: {result['daily']} tons  
        📅 **Monthly Emissions**: {result['monthly']} tons  
        📊 **Yearly Emissions**: {result['yearly']} tons
        """)
        st.subheader("📌 Breakdown (Monthly Estimate in tons)")
        for k, v in result["breakdown"].items():
            st.markdown(f"- **{k}**: {v}")

    st.subheader("🌱 Tips to Reduce Emissions")
    with st.expander("💡 Smart Tips"):
        st.markdown("""
        - 🚶 Walk, cycle, or carpool for daily travel.
        - 💡 Use energy-efficient appliances.
        - 🍽️ Reduce food waste and try plant-based diets.
        - 🚿 Reduce water waste (shorter showers, fix leaks).
        - 🌍 Fly less and use alternatives when possible.
        """)
    with st.expander("📈 Track Your Progress"):
        st.markdown("""
        - 📒 Keep a personal log of your monthly emissions.
        - 🏆 Set targets (e.g., reduce by 5% every month).
        - 📉 Measure reduction by comparing breakdowns.
        """)


# ----------------------------
# ----------------------------
# 3. EMISSION BREAKDOWN (Linked to Calculator)
elif page == "📊 Emission Breakdown":
    st.title("📊 Emission Breakdown (Based on Calculator)")
    st.markdown("Input your values to see the **Daily, Monthly, and Yearly CO₂ emission** summary:")

    col1, col2 = st.columns(2)
    with col1:
        cng = st.slider("🚖 Daily CNG Usage (km)", 0.0, 100.0, 10.0)
        bus = st.slider("🚌 Daily Bus Usage (km)", 0.0, 100.0, 10.0)
        uber = st.slider("🚗 Daily Uber Usage (km)", 0.0, 50.0, 5.0)
        bike = st.slider("🚲 Daily Bicycle Usage (km)", 0.0, 50.0, 5.0)
        motorbike = st.slider("🏍️ Daily Motorbike Usage (km)", 0.0, 50.0, 5.0)
        air = st.slider("✈️ Monthly Air Travel (km)", 0.0, 3000.0, 0.0)
    with col2:
        elec = st.slider("🔌 Monthly Electricity Usage (kWh)", 0.0, 1000.0, 200.0)
        lpg = st.slider("⛽ Monthly LPG Usage (kg)", 0.0, 50.0, 5.0)
        water = st.slider("🚿 Daily Water Usage (liters)", 0.0, 500.0, 100.0)
        meals = st.number_input("🍱 Daily Meals (person)", 1, 10, 3)
        waste = st.slider("🗑️ Weekly Waste Generation (kg)", 0.0, 50.0, 5.0)

    # Emission Factors (kg CO₂ per unit)
    EF = {
        "CNG": 0.055, "Bus": 0.028, "Uber": 0.14,
        "Bike": 0.005, "Motorbike": 0.08, "Air": 0.25,
        "Electricity": 0.62, "LPG": 1.5, "Water": 0.0003,
        "Diet": 1.15, "Waste": 0.09
    }

    # Daily Emission (in kg)
    daily = {
        "CNG": EF["CNG"] * cng,
        "Bus": EF["Bus"] * bus,
        "Uber": EF["Uber"] * uber,
        "Bike": EF["Bike"] * bike,
        "Motorbike": EF["Motorbike"] * motorbike,
        "Water": EF["Water"] * water,
        "Diet": EF["Diet"] * meals
    }

    # Monthly Emission (in kg)
    monthly = {
        "CNG": daily["CNG"] * 30,
        "Bus": daily["Bus"] * 30,
        "Uber": daily["Uber"] * 30,
        "Bike": daily["Bike"] * 30,
        "Motorbike": daily["Motorbike"] * 30,
        "Water": daily["Water"] * 30,
        "Diet": daily["Diet"] * 30,
        "Air": EF["Air"] * air,
        "Electricity": EF["Electricity"] * elec,
        "LPG": EF["LPG"] * lpg,
        "Waste": EF["Waste"] * waste * 4
    }

    # Yearly Emission (in kg)
    yearly = {k: v * 12 for k, v in monthly.items()}

    # Convert to tons
    tons_daily = {k: round((daily.get(k, 0)) / 1000, 4) for k in monthly.keys()}
    tons_monthly = {k: round(v / 1000, 3) for k, v in monthly.items()}
    tons_yearly = {k: round(v / 1000, 3) for k, v in yearly.items()}

    total_daily = round(sum(tons_daily.values()), 4)
    total_monthly = round(sum(tons_monthly.values()), 3)
    total_yearly = round(sum(tons_yearly.values()), 3)

    st.success(f"""
    🌍 **Your Estimated Emissions**  
    - 🗓️ Daily: `{total_daily} tons CO₂`  
    - 📆 Monthly: `{total_monthly} tons CO₂`  
    - 📅 Yearly: `{total_yearly} tons CO₂`
    """)

    # Pie Chart for Monthly Emissions
    st.markdown("### 📊 Monthly Emission Composition (Pie Chart)")
    fig1, ax1 = plt.subplots()
    ax1.pie(tons_monthly.values(), labels=tons_monthly.keys(), autopct="%1.1f%%", startangle=140)
    ax1.axis("equal")
    st.pyplot(fig1)

    # Bar Chart (Seaborn) for Daily, Monthly, Yearly
    st.markdown("### 📊 Emission Comparison (Bar Chart)")

    df_bar = pd.DataFrame({
        "Source": list(tons_monthly.keys()),
        "Daily (tons)": [tons_daily.get(k, 0) for k in tons_monthly.keys()],
        "Monthly (tons)": list(tons_monthly.values()),
        "Yearly (tons)": list(tons_yearly.values())
    })

    df_melted = df_bar.melt(id_vars="Source", var_name="Period", value_name="Tons CO₂")

    fig2 = plt.figure(figsize=(10, 6))
    sns.barplot(data=df_melted, x="Source", y="Tons CO₂", hue="Period")
    plt.xticks(rotation=45)
    plt.title("Emission Comparison by Source")
    st.pyplot(fig2)

    # Table View
    with st.expander("📋 Detailed Emission Breakdown Table (tons)"):
        st.dataframe(df_bar.set_index("Source"), use_container_width=True)



# ----------------------------
# 4. DUCKDUCKGO ECO SEARCH
# ----------------------------
elif page == "🔍 Eco Search":
    st.title("🔍 Eco Search")

    DUCKDUCKGO_API = "https://api.duckduckgo.com/"
    query = st.text_input("Search eco-friendly topics:")

    if st.button("Search DuckDuckGo"):
        if not query.strip():
            st.warning("❗ Please enter a search term.")
        else:
            try:
                response = requests.get(DUCKDUCKGO_API, params={
                    "q": query,
                    "format": "json",
                    "no_redirect": 1,
                    "no_html": 1
                })
                data = response.json()

                abstract = data.get("Abstract", "").strip()
                related = data.get("RelatedTopics", [])

                if abstract:
                    st.markdown(f"🔹 **Summary**: {abstract}")
                elif related:
                    valid_links = [item for item in related if isinstance(item, dict) and "Text" in item and "FirstURL" in item]
                    if valid_links:
                        st.markdown("🔗 **Related Links:**")
                        for item in valid_links[:5]:
                            st.markdown(f"- [{item['Text']}]({item['FirstURL']})")
                    else:
                        st.info("📭 No relevant information found for your query.")
                else:
                    st.info("📭 No relevant information found for your query.")

            except Exception as e:
                st.error(f"🚫 Search error: {e}")

# ----------------------------
# 5. AI ASSISTANT PAGE
# ----------------------------
elif page == "🤖 Eco AI Assistant":
    st.title("🤖 Ask Eco AI (Offline Model)")

    prompt = st.text_area("Ask something about eco-friendly practices, climate, Bangladesh policies, etc.")
    if st.button("Get AI Answer"):
        if not prompt:
            st.warning("Please enter a question for the AI.")
        else:
            try:
                response = requests.post(OLLAMA_URL, json={
                    "model": OLLAMA_MODEL,
                    "prompt": f"You are a helpful AI environmental assistant in Bangladesh.\n\nQuestion: {prompt}\n\nAnswer:",
                    "stream": False
                })
                if response.status_code == 200:
                    result = response.json()
                    reply = result.get("response", "").strip()
                    if reply:
                        st.markdown(f"**AI says:** {reply}")
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                                gTTS(reply).save(tmp.name)
                                st.audio(tmp.name)
                                time.sleep(2)
                                os.remove(tmp.name)
                        except Exception as audio_err:
                            st.error(f"Audio error: {audio_err}")
                    else:
                        st.warning("⚠️ AI did not return a response.")
                else:
                    st.error(f"❌ Ollama server error: {response.status_code}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# ----------------------------
# 6. TASKS & REWARDS
elif page == "✅ Tasks & Rewards":
    st.title("✅ Daily Eco Tasks & Quiz")

    # Get today's date
    today = datetime.now().date()

    # Initialize session state
    if "task_date" not in st.session_state or st.session_state.task_date != today:
        st.session_state.daily_tasks = [
            {"task": "Turn off lights when not in use", "done": False},
            {"task": "Use a reusable water bottle", "done": False},
            {"task": "Walk or cycle instead of using a car", "done": False},
            {"task": "Avoid using plastic bags", "done": False},
            {"task": "Unplug unused devices", "done": False}
        ]
        st.session_state.task_date = today

    if "custom_tasks" not in st.session_state:
        st.session_state.custom_tasks = []

    if "rewards" not in st.session_state:
        st.session_state.rewards = 0

    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0

    if "quiz_date" not in st.session_state:
        st.session_state.quiz_date = None

    # Section: Daily Tasks
    st.header("📝 Today's Eco Tasks")

    st.subheader("📌 Assigned Tasks")
    for i, task in enumerate(st.session_state.daily_tasks):
        col1, col2 = st.columns([0.8, 0.2])
        col1.markdown(f"- {task['task']}")
        done = col2.checkbox("Done", key=f"daily_task_{i}", value=task["done"])
        if done and not task["done"]:
            st.session_state.daily_tasks[i]["done"] = True
            st.session_state.rewards += 1

    st.subheader("➕ Add Your Own Task")
    new_task = st.text_input("Enter your own eco task:")
    if st.button("Add Task") and new_task:
        st.session_state.custom_tasks.append({"task": new_task, "done": False})

    st.subheader("📋 Custom Task List")
    for i, task in enumerate(st.session_state.custom_tasks):
        col1, col2 = st.columns([0.8, 0.2])
        col1.markdown(f"- {task['task']}")
        done = col2.checkbox("Done", key=f"custom_task_{i}", value=task["done"])
        if done and not task["done"]:
            st.session_state.custom_tasks[i]["done"] = True
            st.session_state.rewards += 1

    st.markdown("---")
    st.subheader("🌱 Environmental Awareness Quiz (10 Questions)")

    # Quiz questions
    quiz_questions = [
        {
            "question": "Which of the following vehicles has the least carbon emissions?",
            "options": ["Diesel Car", "Electric Scooter", "Petrol Bike", "Gasoline SUV"],
            "answer": "Electric Scooter"
        },
        {
            "question": "What gas do plants absorb from the atmosphere?",
            "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
            "answer": "Carbon Dioxide"
        },
        {
            "question": "Which of these is a renewable energy source?",
            "options": ["Coal", "Solar", "Oil", "Natural Gas"],
            "answer": "Solar"
        },
        {
            "question": "Which material is NOT biodegradable?",
            "options": ["Banana Peel", "Plastic Bottle", "Paper", "Cotton Cloth"],
            "answer": "Plastic Bottle"
        },
        {
            "question": "What is the biggest contributor to climate change?",
            "options": ["Plastic", "Water Waste", "Greenhouse Gas Emissions", "Noise Pollution"],
            "answer": "Greenhouse Gas Emissions"
        },
        {
            "question": "Which of these actions helps reduce air pollution?",
            "options": ["Using public transport", "Burning trash", "Using diesel cars", "Cutting trees"],
            "answer": "Using public transport"
        },
        {
            "question": "What can you do to conserve water?",
            "options": ["Leave tap open", "Fix leaking taps", "Use bathtub daily", "Water lawn daily"],
            "answer": "Fix leaking taps"
        },
        {
            "question": "Which of the following is an eco-friendly habit?",
            "options": ["Throwing plastic into rivers", "Using reusable bags", "Driving solo daily", "Leaving lights on"],
            "answer": "Using reusable bags"
        },
        {
            "question": "Which mode of transport is most eco-friendly?",
            "options": ["Walking", "SUV", "Motorcycle", "Airplane"],
            "answer": "Walking"
        },
        {
            "question": "What does 'reduce' in the 3Rs mean?",
            "options": ["Use less", "Throw away", "Recycle more", "Buy more"],
            "answer": "Use less"
        }
    ]

    # Shuffle and check daily quiz attempt
    random.shuffle(quiz_questions)

    if st.session_state.quiz_date != today:
        user_answers = []
        for i, q in enumerate(quiz_questions[:10]):
            st.write(f"**Q{i+1}. {q['question']}**")
            user_choice = st.radio("", q["options"], key=f"quiz_q{i}")
            user_answers.append((user_choice, q["answer"]))

        if st.button("Submit Quiz"):
            score = 0
            for user_ans, correct_ans in user_answers:
                if user_ans == correct_ans:
                    score += 2
            st.success(f"🎉 You scored {score} points in today's quiz!")
            st.session_state.quiz_score = score
            st.session_state.rewards += score
            st.session_state.quiz_date = today
    else:
        st.info(f"✅ You already completed today's quiz. You earned: {st.session_state.quiz_score} points.")

    # Final reward display
    st.markdown("---")
    st.success(f"🏆 Total Rewards Earned: {st.session_state.rewards} points")

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")

footer = """
<style>
.footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background-color: #f0f2f6;
    color: #333;
    text-align: center;
    padding: 10px 0;
    font-size: 14px;
    border-top: 1px solid #ccc;
}
.footer a {
    color: #4CAF50;
    text-decoration: none;
    font-weight: 500;
}
.footer a:hover {
    text-decoration: underline;
}
</style>

<div class="footer">
    🌿 Made with ❤️ by <a href="https://github.com/saha6754" target="_blank">Suvo Saha</a> | 🕒 Last updated: {update_time}
</div>
"""
st.caption(f"🕒 Last updated: {datetime.now():%Y-%m-%d %H:%M:%S}")



















