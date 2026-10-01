import streamlit as st
from datetime import datetime, date
import os

# Optional Groq import
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Age Calculator",
    page_icon="🎂",
    layout="centered"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.main {
    padding-top: 2rem;
}

.title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    margin-bottom: 30px;
}

.age-box {
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin-top: 20px;
}

.big-age {
    font-size: 40px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="title">🎂 Age Calculator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Calculate your exact age in years, months, days, hours, minutes and seconds.'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# DATE OF BIRTH
# --------------------------------------------------

st.subheader("📅 Enter Your Date of Birth")

dob = st.date_input(
    "Date of Birth",
    min_value=date(1900, 1, 1),
    max_value=date.today(),
    value=date(2000, 1, 1)
)


# --------------------------------------------------
# CALCULATE AGE
# --------------------------------------------------

def calculate_age(birth_date):

    now = datetime.now()
    birth_datetime = datetime.combine(birth_date, datetime.min.time())

    # Total difference
    difference = now - birth_datetime

    total_seconds = int(difference.total_seconds())

    years = now.year - birth_date.year
    months = now.month - birth_date.month
    days = now.day - birth_date.day

    if days < 0:

        months -= 1

        if now.month == 1:
            previous_month = 12
            previous_year = now.year - 1
        else:
            previous_month = now.month - 1
            previous_year = now.year

        import calendar

        days += calendar.monthrange(
            previous_year,
            previous_month
        )[1]

    if months < 0:
        years -= 1
        months += 12

    # Calculate hours/minutes/seconds
    remaining_seconds = total_seconds

    hours = remaining_seconds // 3600
    minutes = (remaining_seconds % 3600) // 60
    seconds = remaining_seconds % 60

    return (
        years,
        months,
        days,
        hours,
        minutes,
        seconds,
        total_seconds
    )


# --------------------------------------------------
# BUTTON
# --------------------------------------------------

if st.button(
    "🔢 Calculate My Age",
    type="primary",
    use_container_width=True
):

    today = date.today()

    if dob > today:

        st.error("❌ Date of birth cannot be in the future.")

    else:

        (
            years,
            months,
            days,
            hours,
            minutes,
            seconds,
            total_seconds
        ) = calculate_age(dob)

        # ------------------------------------------
        # MAIN AGE
        # ------------------------------------------

        st.success("🎉 Your Age")

        st.markdown(
            f"""
            <div class="age-box">

            <div class="big-age">
            {years} Years {months} Months {days} Days
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        # ------------------------------------------
        # DETAILED AGE
        # ------------------------------------------

        st.subheader("⏱️ Detailed Age")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Years", years)
            st.metric("Days", days)

        with col2:
            st.metric("Months", months)
            st.metric("Hours", hours)

        with col3:
            st.metric("Minutes", minutes)
            st.metric("Seconds", seconds)

        st.divider()

        # ------------------------------------------
        # TOTAL VALUES
        # ------------------------------------------

        st.subheader("📊 Total Age")

        total_minutes = total_seconds // 60
        total_hours = total_seconds // 3600
        total_days = total_seconds // 86400

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"🗓️ **Total Days:** {total_days:,}")
            st.info(f"⏰ **Total Hours:** {total_hours:,}")

        with col2:
            st.info(f"⏱️ **Total Minutes:** {total_minutes:,}")
            st.info(f"⚡ **Total Seconds:** {total_seconds:,}")


        # ------------------------------------------
        # BIRTHDAY INFORMATION
        # ------------------------------------------

        st.divider()

        st.subheader("🎁 Birth Information")

        st.write(
            f"**Date of Birth:** "
            f"{dob.strftime('%d %B %Y')}"
        )

        st.write(
            f"**Current Date:** "
            f"{today.strftime('%d %B %Y')}"
        )


# --------------------------------------------------
# GROQ AI SECTION
# --------------------------------------------------

st.divider()

st.subheader("🤖 AI Age Assistant")

st.write(
    "Ask the AI assistant something about your age, birthday, "
    "or age calculation."
)

question = st.text_input(
    "Ask a question",
    placeholder="Example: What is interesting about my age?"
)


if question:

    # Get Groq API key from Streamlit secrets
    groq_api_key = None

    try:
        groq_api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:

        st.warning(
            "⚠️ GROQ_API_KEY is not configured. "
            "The calculator itself works without the Groq API."
        )

    elif not GROQ_AVAILABLE:

        st.error(
            "Groq package is not installed. "
            "Add groq to requirements.txt."
        )

    else:

        try:

            client = Groq(
                api_key=groq_api_key
            )

            response = client.chat.completions.create(

                model="openai/gpt-oss-120b",

                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful age and birthday assistant. "
                            "Give concise, friendly and accurate answers."
                        )
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],

                temperature=0.3
            )

            answer = response.choices[0].message.content

            st.markdown("### 🤖 AI Response")
            st.write(answer)

        except Exception as e:

            st.error(
                f"Unable to contact Groq API: {str(e)}"
            )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "🎂 Age Calculator | Built with Python + Streamlit + Groq"
)
