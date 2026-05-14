import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(
    page_title="Employee of the Year Voting",
    page_icon="🏆",
    layout="centered"
)

DB_NAME = "votes.db"
ADMIN_PASSWORD = "admin123"  # Change this before sharing the app
SCORE_PER_VOTE = 10

EMPLOYEES = [
    "EDA",
    "ERKAN",
    "ERGUN",
    "ERSİN",
    "GÜLAY",
    "ALPAY",
    "NURCİHAN",
    "ZEYNEP"
]

QUESTIONS = [
    {
        "id": 1,
        "category": "Proactive Approach",
        "en": "Who stood out the most with their proactive approach this year?",
        "tr": "Bu yıl proaktif yaklaşımıyla, yani sorun çıkmadan önce aksiyon alması ve işleri önceden takip etmesiyle en çok kim öne çıktı?"
    },
    {
        "id": 2,
        "category": "Ownership & Responsibility",
        "en": "Who stood out the most in taking ownership and following up on their responsibilities?",
        "tr": "İşlerini sahiplenme, sorumluluk alma ve konuları sonuca kadar takip etme konusunda en çok kim öne çıktı?"
    },
    {
        "id": 3,
        "category": "Team Support",
        "en": "Who was the strongest in supporting their teammates?",
        "tr": "Ekip arkadaşlarına destek olma, yardım etme ve gerektiğinde yanında olma konusunda en güçlü kişi kimdi?"
    },
    {
        "id": 4,
        "category": "Problem Solving",
        "en": "Who was the most effective in finding solutions during challenging situations?",
        "tr": "Zor veya beklenmedik durumlarda çözüm üretme ve problemi yönetme konusunda en etkili kişi kimdi?"
    },
    {
        "id": 5,
        "category": "Communication & Positive Attitude",
        "en": "Who contributed the most with their communication skills and positive attitude?",
        "tr": "Ekip içindeki iletişimi, yapıcı yaklaşımı ve pozitif tutumuyla en çok katkı sağlayan kişi kimdi?"
    },
    {
        "id": 6,
        "category": "Work Quality",
        "en": "Who stood out the most by completing their work accurately, consistently, and on time?",
        "tr": "İşlerini doğru, düzenli, tutarlı ve zamanında tamamlama konusunda en çok kim öne çıktı?"
    },
    {
        "id": 7,
        "category": "Growth & Contribution",
        "en": "Who made the biggest difference this year through their growth, ideas, or contribution to the process?",
        "tr": "Bu yıl gelişimi, fikirleri veya süreçlere sağladığı katkılarla en çok fark yaratan kişi kimdi?"
    },
    {
        "id": 8,
        "category": "Team Spirit",
        "en": "Who contributed the most to the team spirit this year?",
        "tr": "Bu yıl ekip ruhuna en çok katkı sağlayan kişi kimdi?"
    },
    {
        "id": 9,
        "category": "Reliability",
        "en": "Who was the most reliable person when things needed to get done?",
        "tr": "İşlerin tamamlanması gerektiğinde en güvenilir kişi kimdi?"
    },
    {
        "id": 10,
        "category": "Overall Impact",
        "en": "Who made the strongest overall impact on the team this year?",
        "tr": "Bu yıl ekip üzerinde genel olarak en güçlü etkiyi kim yarattı?"
    }
]

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter TEXT NOT NULL,
            nickname TEXT NOT NULL,
            question_id INTEGER NOT NULL,
            question_category TEXT NOT NULL,
            selected_person TEXT NOT NULL,
            score INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def has_voted(voter):
    conn = get_connection()
    query = "SELECT COUNT(*) FROM votes WHERE voter = ?"
    count = pd.read_sql_query(query, conn, params=(voter,)).iloc[0, 0]
    conn.close()
    return count > 0

def save_votes(voter, nickname, answers):
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for question in QUESTIONS:
        question_id = question["id"]
        selected_person = answers[question_id]
        cursor.execute(
            """
            INSERT INTO votes (
                voter, nickname, question_id, question_category,
                selected_person, score, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                voter,
                nickname,
                question_id,
                question["category"],
                selected_person,
                SCORE_PER_VOTE,
                created_at
            )
        )

    conn.commit()
    conn.close()

def load_votes():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM votes", conn)
    conn.close()
    return df

def reset_votes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM votes")
    conn.commit()
    conn.close()

def calculate_total_scores(votes_df):
    if votes_df.empty:
        return pd.DataFrame(columns=["selected_person", "score"])

    return (
        votes_df
        .groupby("selected_person", as_index=False)["score"]
        .sum()
        .sort_values("score", ascending=False)
    )

def calculate_winner(votes_df):
    total_scores = calculate_total_scores(votes_df)
    if total_scores.empty:
        return None, 0

    winner = total_scores.iloc[0]["selected_person"]
    winner_score = int(total_scores.iloc[0]["score"])
    return winner, winner_score

def calculate_category_winners(votes_df):
    if votes_df.empty:
        return pd.DataFrame(columns=["question_category", "selected_person", "score"])

    category_scores = (
        votes_df
        .groupby(["question_category", "selected_person"], as_index=False)["score"]
        .sum()
        .sort_values(["question_category", "score"], ascending=[True, False])
    )

    return (
        category_scores
        .groupby("question_category")
        .head(1)
        .reset_index(drop=True)
    )

create_tables()

st.title("🏆 A Look Back at Our Year Together")
st.caption("Anonymous Employee of the Year Voting")

st.markdown(
    """
    Let's reflect on the moments, efforts, and team spirit that shaped this year.  
    Bu yıl birlikte yaşadığımız anları, gösterilen emekleri ve ekip ruhunu kısa ve eğlenceli bir şekilde hatırlıyoruz.
    """
)

menu = st.sidebar.radio(
    "Menu",
    ["Vote", "Final Result", "Admin"]
)

if menu == "Vote":
    st.header("🗳️ Vote / Oy Kullan")

    voter = st.selectbox(
        "1. Select your real name / Gerçek ismini seç",
        options=["Select / Seç"] + EMPLOYEES
    )

    nickname = st.text_input(
        "2. Write your nickname / Nickname yaz",
        placeholder="Example: BlueTiger"
    )

    if voter != "Select / Seç":
        if has_voted(voter):
            st.error("Bu isim daha önce oy kullandı. Each real name can vote only once.")
        else:
            st.info("Kendi adına oy veremezsin. Your own name will not appear in the options.")

            available_options = [person for person in EMPLOYEES if person != voter]
            answers = {}

            st.divider()

            with st.form("voting_form"):
                for question in QUESTIONS:
                    st.subheader(f"Question {question['id']} — {question['category']}")
                    st.write(f"**EN:** {question['en']}")
                    st.write(f"**TR:** {question['tr']}")

                    selected_person = st.selectbox(
                        "Choose one person / Bir kişi seç",
                        options=["Select / Seç"] + available_options,
                        key=f"question_{question['id']}"
                    )

                    answers[question["id"]] = selected_person
                    st.divider()

                submitted = st.form_submit_button("Submit My Vote / Oyumu Gönder")

                if submitted:
                    if not nickname.strip():
                        st.error("Lütfen nickname yaz.")
                    elif any(value == "Select / Seç" for value in answers.values()):
                        st.error("Lütfen tüm sorular için bir kişi seç.")
                    elif has_voted(voter):
                        st.error("Bu isim daha önce oy kullandı.")
                    else:
                        save_votes(voter, nickname.strip(), answers)
                        st.success("Oyun başarıyla kaydedildi. Thank you for voting!")
                        st.balloons()
    else:
        st.warning("Oy kullanmak için önce gerçek ismini seçmelisin.")

elif menu == "Final Result":
    st.header("🏆 Final Result / Final Sonuç")

    votes_df = load_votes()
    winner, winner_score = calculate_winner(votes_df)

    if winner is None:
        st.info("Henüz oy yok. No votes yet.")
    else:
        st.success("Employee of the Year / Yılın Elemanı")
        st.markdown(f"# 🏆 {winner}")
        st.metric("Total Score / Toplam Puan", winner_score)
        st.caption("Only the final winner is shown here. Detailed results are visible only in the admin panel.")

elif menu == "Admin":
    st.header("🔐 Admin Panel")

    password = st.text_input("Admin password", type="password")

    if password == ADMIN_PASSWORD:
        votes_df = load_votes()

        st.success("Admin access granted.")

        if votes_df.empty:
            st.info("Henüz oy yok.")
        else:
            total_voters = votes_df["voter"].nunique()
            total_votes = len(votes_df)
            total_points = votes_df["score"].sum()
            winner, winner_score = calculate_winner(votes_df)

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Voters", total_voters)
            col2.metric("Total Votes", total_votes)
            col3.metric("Total Points", total_points)

            st.divider()

            st.subheader("Final Winner")
            st.markdown(f"## 🏆 {winner}")
            st.metric("Winner Score", winner_score)

            st.divider()

            st.subheader("Total Scores — Admin Only")
            total_scores = calculate_total_scores(votes_df)
            st.dataframe(total_scores, use_container_width=True)
            st.bar_chart(total_scores.set_index("selected_person"))

            st.divider()

            st.subheader("Category Winners — Admin Only")
            category_winners = calculate_category_winners(votes_df)
            st.dataframe(category_winners, use_container_width=True)

            st.divider()

            st.subheader("Raw Votes — Admin Only")
            st.warning("Bu tablo kim kime oy verdi bilgisini içerir. Normal sonuç ekranında gösterilmez.")
            st.dataframe(votes_df, use_container_width=True)

            st.divider()

            with st.expander("Danger Zone"):
                st.warning("Bu işlem tüm oyları siler.")
                confirm_reset = st.checkbox("I understand. Delete all votes.")
                if st.button("Reset All Votes"):
                    if confirm_reset:
                        reset_votes()
                        st.success("Tüm oylar silindi. Sayfayı yenileyebilirsin.")
                    else:
                        st.error("Silmek için onay kutusunu işaretlemelisin.")

    elif password:
        st.error("Wrong password.")
    else:
        st.info("Admin sonuçlarını görmek için şifre gir.")
