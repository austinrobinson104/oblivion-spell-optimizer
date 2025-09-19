# app.py
import streamlit as st
import math
def spell_cost(base_cost, mag, duration, area, cost_mult, skill):
    skill_mult = round(1.4 - 0.012 * skill, 3)  # 3 decimal places
    area = area * 0.15
    if area < 1:
        area = 1
    raw = math.floor((base_cost) * (mag**1.28) * duration * area * cost_mult)
    return math.floor(raw * skill_mult)

def damage_after_effectiveness(mag, weight, eff):
    # 95% effectiveness, rounded down
    return math.floor((eff/100.0) * mag) * weight

def brute_force_near_budget(budget, max_mag, duration, area, fire_mult, frost_mult, shock_mult, cost_mult, eff, skill):
    best = (0,0,0,0,0)  # (damage, fire, frost, shock, cost)
    for fire in range(3, max_mag+1):
        fire_cost  = spell_cost(0.75, fire, duration, area, cost_mult, skill)
        fire_dmg   = damage_after_effectiveness(fire, fire_mult, eff)
        if fire_cost > budget: 
            break  # no point increasing further

        for frost in range(3, max_mag+1):
            frost_cost = spell_cost(0.74, frost, duration, area, cost_mult, skill)
            frost_dmg  = damage_after_effectiveness(frost, frost_mult, eff)
            if fire_cost + frost_cost > budget:
                break

            for shock in range(3, max_mag+1):
                shock_cost = spell_cost(0.78, shock, duration, area, cost_mult, skill)
                total_cost = fire_cost + frost_cost + shock_cost

                if total_cost > budget: 
                    break

                shock_dmg = damage_after_effectiveness(shock, shock_mult, eff)
                total_dmg = duration * (fire_dmg + frost_dmg + shock_dmg)
                if total_dmg > best[0]:
                    best = (total_dmg, fire, frost, shock, total_cost)
    return best


# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Oblivion Spell Optimizer", page_icon="⚡")

# ---------------- Custom CSS ----------------
st.markdown(
    """
    <style>
    /* Main app background */
    .stApp {
        background-color: #fdf6e3; /* soft yellowish off-white */
        color: #333333; /* dark gray default text */
    }

    /* Headers */
    h1, h2, h3 {
        color: #333333 !important;
    }

    /* Buttons */
    div.stButton > button:first-child {
        background-color: #ffcc66 !important;
        color: black !important;
        border-radius: 8px !important;
        border: 1px solid #b58900 !important;
    }
    div.stButton > button:hover {
        background-color: #ffb84d !important;
        color: black !important;
    }

    /* Success box styling */
    .stSuccess {
        background-color: #fff2cc !important;
        border-left: 6px solid #b58900 !important;
        color: #333 !important;
    }

    /* Success box text color */
    .stSuccess, 
    .stSuccess * {
        color: #222 !important;  /* dark gray */
    }

    /* General input text, sliders, selects, labels */
    body, .stMarkdown, .stSlider, .stNumberInput, .stSelectbox, .stSelectSlider, label {
        color: #222 !important; /* dark gray text */
    }

    /* Force all radio option text to dark gray */
    .stRadio label, 
    .stRadio label div, 
    .stRadio label span {
        color: #222 !important;
    }

    /* Radio button option text */
    .stRadio div[role="radiogroup"] label > div > span {
        color: #222 !important;  /* dark gray */
    }

    /* Adjust placeholder/option text in selects */
    .stSelectbox select, .stSelectSlider div {
        color: #222 !important;
    }

    /* Slider handle and labels */
    .stSlider .e1fqkh3o3, .stSlider label {
        color: #222 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Title Banner ----------------
st.markdown(
    "<h1 style='text-align: center; color: #ff4b4b;'>⚡ Oblivion Spell Optimizer ⚡</h1>",
    unsafe_allow_html=True
)

# ---------------- Inputs ----------------
st.header("📜 Spell Parameters")

# Budget + Duration
budget = st.number_input("🔮 Magicka Budget", min_value=1, max_value=1000, value=100)
duration = st.slider("⏳ Duration (seconds)", 1, 120, 4)

# Area
area = st.select_slider(
    "🌐 Area (0 = N/A, otherwise 10–100)",
    options=[0] + list(range(10, 101)),
    value=0
)

# Cast type
cast_type = st.radio("🎯 Range", ["On Touch (1x cost)", "On Target (1.5x cost)"])
cost_mult = 1.5 if "Target" in cast_type else 1.0

# ---------------- Element multipliers ----------------
st.header("🔥 Element Effectiveness")

fire_mult = st.number_input("🔥 Fire Multiplier", value=1.0, step=0.01)
frost_mult = st.number_input("❄️ Frost Multiplier", value=0.9, step=0.01)
shock_mult = st.number_input("⚡ Shock Multiplier", value=1.1, step=0.01)

# ---------------- Caster Stats ----------------
st.header("🎓 Caster Stats")

skill_raw = st.slider("📘 Skill Level", min_value=0, max_value=100, value=100)

spell_effectiveness = st.select_slider(
    "✨ Spell Effectiveness (%)",
    options=list(range(70, 96)) + [100],
    value=95
)

luck = st.slider("🍀 Luck", min_value=0, max_value=120, value=50)

# Adjust skill with luck
skill = math.floor(skill_raw + (0.4 * (luck - 50)))
if skill > 100:
    skill = 100

if skill < 0:
    skill = 0

# ---------------- Optimize ----------------
st.markdown("---")
if st.button("🔍 Optimize!"):
    best = brute_force_near_budget(
        budget, 100, duration, area,
        fire_mult, frost_mult, shock_mult,
        cost_mult, spell_effectiveness, skill
    )

    st.success(
        f"🔥 **Best Damage = {best[0]}**\n\n"
        f"💰 Cost = {best[4]}\n\n"
        f"🔥 Fire = {best[1]} | ❄️ Frost = {best[2]} | ⚡ Shock = {best[3]}"
    )






