import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Superdry Turkey Office | Employee of the Year",
    page_icon="🏆",
)

# =====================================================
# SETTINGS
# =====================================================

DB_NAME = "votes.db"
ADMIN_PASSWORD = "admin123"        # Limited admin: no voter / nickname info
FULL_ADMIN_PASSWORD = "tokyo123"   # Full admin: shows everything
RESULT_PASSWORD = "winner2026"     # Password for revealing final result
SCORE_PER_VOTE = 10

# Oy kullanabilecek kişiler
VOTERS = [
    "EDA",
    "ERGUN",
    "ERKAN",
    "ERSİN",
    "GÜLAY",
    "NURCİHAN",
    "SERBAY",
    "ZEYNEP"
]

# Oy verilebilecek kişiler
# EDA burada yok, yani EDA oy kullanabilir ama EDA'ya oy verilemez.
EMPLOYEES = [
    "ERGUN",
    "ERKAN",
    "ERSİN",
    "GÜLAY",
    "NURCİHAN",
    "SERBAY",
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
        "category": "Calm Problem Solving",
        "en": "Who stays calm when problems arise and focuses on finding solutions in the most effective way?",
        "tr": "Sorunlar karşısında sakin kalıp en etkili şekilde çözüm üretmeye odaklanan kişi kimdir?"
    },
    {
        "id": 4,
        "category": "Supporting Cross Functions",
        "en": "Who has been the most supportive teammate across cross-functional teams?",
        "tr": "Kendi ekibi dışındaki ekiplerle çalışırken, farklı fonksiyonlara en çok destek olan kişi kimdi?"
    },
    {
        "id": 5,
        "category": "Problem Solving",
        "en": "Who was the most effective in finding solutions during challenging situations?",
        "tr": "Zor veya beklenmedik durumlarda çözüm üretme ve problemi yönetme konusunda en etkili kişi kimdi?"
    },
    {
        "id": 6,
        "category": "Communication & Positive Attitude",
        "en": "Who contributed the most with their communication skills and positive attitude?",
        "tr": "Ekip içindeki iletişimi, yapıcı yaklaşımı ve pozitif tutumuyla en çok katkı sağlayan kişi kimdi?"
    },
    {
        "id": 7,
        "category": "Stress Management",
        "en": "Who is the person you see as a role model for managing stress calmly and professionally?",
        "tr": "Stres yönetimini sakin ve profesyonel şekilde yaptığı için örnek aldığınız kişi kimdir?"
    },
    {
        "id": 8,
        "category": "Work Quality",
        "en": "Who stood out the most by completing their work accurately, consistently, and on time?",
        "tr": "İşlerini doğru, düzenli, tutarlı ve zamanında tamamlama konusunda en çok kim öne çıktı?"
    },
    {
        "id": 9,
        "category": "Team Cheer-Up",
        "en": "Who has been the teammate who always manages to cheer others up?",
        "tr": "Moral gerektiğinde ortamı neşelendiren, ekibi güldüren veya pozitif enerji katan kişi kimdi?"
    },
    {
        "id": 10,
        "category": "Team Spirit",
        "en": "Who contributed the most to the team spirit this year?",
        "tr": "Bu yıl ekip ruhuna en çok katkı sağlayan kişi kimdi?"
    },
    {
        "id": 11,
        "category": "Reliability",
        "en": "Who was the most reliable person when things needed to get done?",
        "tr": "İşlerin tamamlanması gerektiğinde en güvenilir kişi kimdi?"
    },
    {
        "id": 12,
        "category": "Best Use of Communication Tools",
        "en": "Who communicates most proactively and effectively across e-mail, Teams and WhatsApp?",
        "tr": "E-mail, Teams ve WhatsApp gibi iletişim kanallarında en proaktif, etkili ve doğru iletişim kuran kişi kimdi?"
    },
    {
        "id": 13,
        "category": "Most Agile Teammate",
        "en": "Who adapts the quickest when priorities change or new situations come up?",
        "tr": "Öncelikler değiştiğinde veya yeni durumlar ortaya çıktığında en hızlı uyum sağlayan kişi kimdi?"
    },
    {
        "id": 14,
        "category": "Social Spirit",
        "en": "Who has been the most enthusiastic and supportive teammate when it comes to social activities and team plans?",
        "tr": "Sosyal aktiviteler, ekip planları ve birlikte yapılan organizasyonlarda en istekli ve destekleyici kişi kimdi?"
    },
    {
        "id": 15,
        "category": "Important Project Partner",
        "en": "Who would you choose to work with on a highly important project?",
        "tr": "Çok önemli bir projede birlikte çalışmak için bir kişiyi seçmen gerekse, kimi seçerdin?"
    },
    {
        "id": 16,
        "category": "Work Ethic & Dedication",
        "en": "Who has earned your respect with their dedication and strong work ethic?",
        "tr": "Çalışma disiplini, iş etiği ve özverisiyle saygını en çok kazanan kişi kimdi?"
    }
]

# =====================================================
# DESIGN / STYLE
# =====================================================

st.markdown(
    '''
    <style>
    :root {
        --sd-navy: #060D29;
        --sd-teal: #17324F;
        --sd-light-teal: #24506F;
        --sd-off-white: #FFEED9;
        --sd-soft-cream: #FFF7EC;
        --sd-gold: #A77A19;
        --sd-black: #000000;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(167,122,25,0.18), transparent 28%),
            radial-gradient(circle at bottom right, rgba(255,238,217,0.35), transparent 34%),
            linear-gradient(135deg, #16324F 0%, #24506F 48%, #FFF1DD 100%);
        color: var(--sd-off-white);
    }

    .main .block-container {
        max-width: 980px;
        padding-top: 2.4rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: var(--sd-navy);
        border-right: 1px solid rgba(167,122,25,0.45);
    }

    [data-testid="stSidebar"] * {
        color: var(--sd-off-white) !important;
    }

    h1, h2, h3 {
        color: var(--sd-off-white) !important;
        font-weight: 900 !important;
    }

    p, label, span {
        font-size: 16px;
    }

    .app-hero {
        background: rgba(6,13,41,0.82);
        border: 1px solid rgba(167,122,25,0.65);
        border-radius: 30px;
        padding: 34px 36px;
        text-align: center;
        box-shadow: 0 20px 55px rgba(0,0,0,0.32);
        margin-bottom: 28px;
    }

    .hero-title {
        color: var(--sd-off-white);
        font-size: 42px;
        font-weight: 950;
        letter-spacing: 2px;
        line-height: 1.15;
        margin-bottom: 12px;
    }

    .hero-kicker {
        color: var(--sd-off-white);
        font-size: 18px;
        font-weight: 800;
        margin-top: 8px;
        margin-bottom: 24px;
    }

    .hero-subtitle {
        color: rgba(255,238,217,0.95);
        font-size: 16.5px;
        line-height: 1.65;
    }

    .gold-line {
        height: 4px;
        width: 130px;
        background: var(--sd-gold);
        border-radius: 999px;
        margin: 18px auto;
    }

    .rule-wrapper {
        display: flex;
        gap: 14px;
        margin: 18px 0 28px 0;
        flex-wrap: wrap;
    }

    .rule-card {
        flex: 1;
        min-width: 185px;
        background: rgba(255,238,217,0.94);
        border: 1px solid rgba(167,122,25,0.55);
        border-radius: 20px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.14);
    }

    .rule-icon {
        font-size: 26px;
        margin-bottom: 6px;
    }

    .rule-title {
        color: var(--sd-black);
        font-weight: 900;
        font-size: 17px;
    }

    .rule-text {
        color: var(--sd-navy);
        font-size: 14px;
        margin-top: 3px;
    }

    .section-card {
        background: rgba(255,238,217,0.95);
        border: 1px solid rgba(167,122,25,0.55);
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 14px 38px rgba(0,0,0,0.20);
        margin: 18px 0 26px 0;
    }

    .section-card-title {
        color: var(--sd-navy);
        font-size: 22px;
        font-weight: 900;
        margin-bottom: 8px;
    }

    .section-card-subtitle {
        color: rgba(6,13,41,0.75);
        font-size: 15px;
        margin-bottom: 18px;
    }

    .question-card {
        background: rgba(255,238,217,0.94);
        border: 1px solid rgba(167,122,25,0.42);
        border-radius: 20px;
        padding: 18px 18px 6px 18px;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }

    .question-title {
        color: var(--sd-navy);
        font-weight: 900;
        font-size: 20px;
        margin-bottom: 8px;
    }

    .question-text {
        color: var(--sd-navy);
        font-size: 15.5px;
        line-height: 1.55;
        margin-bottom: 10px;
    }

    .soft-card {
        background: rgba(255,238,217,0.94);
        border: 1px solid rgba(167,122,25,0.55);
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 12px 35px rgba(0,0,0,0.22);
        margin-bottom: 18px;
        color: var(--sd-navy);
    }

    .soft-card * {
        color: var(--sd-navy) !important;
    }

    .top-three-box {
        background: rgba(255,238,217,0.96);
        border: 1px solid rgba(167,122,25,0.65);
        border-radius: 26px;
        padding: 28px;
        text-align: center;
        box-shadow: 0 16px 42px rgba(0,0,0,0.25);
        margin: 22px 0;
    }

    .top-three-box * {
        color: #060D29 !important;
    }

    .winner-box {
        background:
            radial-gradient(circle at top, rgba(255,238,217,0.96), rgba(167,122,25,0.92)),
            linear-gradient(135deg, #A77A19, #c89b3d);
        color: var(--sd-black);
        padding: 46px 30px;
        border-radius: 34px;
        text-align: center;
        box-shadow: 0 24px 70px rgba(0,0,0,0.45);
        border: 2px solid rgba(255,238,217,0.85);
        margin-top: 28px;
    }

    .winner-box * {
        color: var(--sd-black) !important;
    }

    .winner-label {
        font-size: 24px;
        font-weight: 850;
    }

    .winner-name {
        font-size: 58px;
        font-weight: 950;
        margin: 18px 0 8px 0;
        letter-spacing: 4px;
    }

    .winner-score {
        font-size: 26px;
        font-weight: 850;
    }

    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] {
        background-color: #FFF7EC !important;
        color: var(--sd-black) !important;
        border-radius: 12px !important;
    }

    .stRadio label {
        color: var(--sd-navy) !important;
        font-weight: 800 !important;
    }

    .stRadio div[role="radiogroup"] {
        background: rgba(255,247,236,0.72);
        border: 1px solid rgba(167,122,25,0.35);
        border-radius: 16px;
        padding: 12px;
    }

    .stTextArea textarea {
        background-color: #FFF7EC !important;
        color: var(--sd-black) !important;
        border-radius: 12px !important;
    }

    .stButton > button {
        background: var(--sd-gold);
        color: var(--sd-black);
        border: 1px solid rgba(255,238,217,0.55);
        border-radius: 14px;
        font-weight: 850;
        padding: 0.65rem 1.1rem;
    }

    .stButton > button:hover {
        background: var(--sd-off-white);
        color: var(--sd-black);
        border: 1px solid var(--sd-gold);
    }

    .stAlert {
        border-radius: 16px;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,238,217,0.92);
        border: 1px solid rgba(167,122,25,0.45);
        border-radius: 16px;
        padding: 12px;
    }

    hr {
        border-color: rgba(167,122,25,0.35);
    }
    </style>
    ''',
    unsafe_allow_html=True
)

# =====================================================
# DATABASE FUNCTIONS
# =====================================================

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter TEXT NOT NULL,
            nickname TEXT NOT NULL,
            question_id INTEGER NOT NULL,
            question_category TEXT NOT NULL,
            selected_person TEXT NOT NULL,
            comment TEXT NOT NULL DEFAULT '',
            score INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        '''
    )

    cursor.execute("PRAGMA table_info(votes)")
    columns = [column[1] for column in cursor.fetchall()]

    if "comment" not in columns:
        cursor.execute("ALTER TABLE votes ADD COLUMN comment TEXT NOT NULL DEFAULT ''")

    conn.commit()
    conn.close()


def has_voted(voter):
    conn = get_connection()
    query = "SELECT COUNT(*) FROM votes WHERE voter = ?"
    count = pd.read_sql_query(query, conn, params=(voter,)).iloc[0, 0]
    conn.close()
    return count > 0


def save_votes(voter, nickname, answers, comments):
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for question in QUESTIONS:
        question_id = question["id"]
        selected_person = answers[question_id]
        comment = comments[question_id]

        cursor.execute(
            '''
            INSERT INTO votes (
                voter,
                nickname,
                question_id,
                question_category,
                selected_person,
                comment,
                score,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                voter,
                nickname,
                question_id,
                question["category"],
                selected_person,
                comment,
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


# =====================================================
# RESULT FUNCTIONS
# =====================================================

def calculate_total_scores(votes_df):
    if votes_df.empty:
        return pd.DataFrame(columns=["selected_person", "score"])

    return (
        votes_df
        .groupby("selected_person", as_index=False)["score"]
        .sum()
        .sort_values(["score", "selected_person"], ascending=[False, True])
        .reset_index(drop=True)
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
        .sort_values(["question_category", "score", "selected_person"], ascending=[True, False, True])
    )

    return (
        category_scores
        .groupby("question_category")
        .head(1)
        .reset_index(drop=True)
    )


def calculate_top_3_people_only(votes_df):
    """
    Sadece ilk 3 kişiyi gösterir.
    4. kişi 3. kişiyle aynı puanda olsa bile dahil edilmez.
    İlk 3 kişinin kendi içinde eşit puanı varsa aynı sırada gösterilir.
    """
    if votes_df.empty:
        return pd.DataFrame(columns=["selected_person", "score", "rank"])

    total_scores = calculate_total_scores(votes_df).copy()

    top_3 = total_scores.head(3).copy().reset_index(drop=True)

    unique_scores = top_3["score"].drop_duplicates().tolist()

    score_to_rank = {
        score: rank + 1
        for rank, score in enumerate(unique_scores)
    }

    top_3["rank"] = top_3["score"].map(score_to_rank)

    return top_3


# =====================================================
# APP START
# =====================================================

create_tables()

menu = st.sidebar.radio(
    "Menu",
    ["Vote", "Final Result", "Admin"]
)


def show_vote_hero():
    st.markdown(
        '''
        <div class="app-hero">
            <div class="hero-title">🏆 SUPERDRY TURKEY OFFICE</div>
            <div class="gold-line"></div>
            <div class="hero-kicker">Employee of the Year Voting</div>
            <div class="hero-subtitle">
                This year, every team member contributed in their own way with effort, support, responsibility, and team spirit.
                Each contribution helped make our office stronger, more positive, and more connected.<br><br>
                Now, as a small and meaningful celebration of our shared year, we are choosing the colleague who stood out just a little more
                with their impact, dedication, and positive energy.<br><br>
                Bu yıl her ekip arkadaşımız emeği, desteği, sorumluluk bilinci ve ekip ruhuyla kendi yolunda değer kattı.
                Her katkı ofisimizi daha güçlü, daha pozitif ve daha bağlı hale getirdi.<br><br>
                Şimdi, birlikte geçirdiğimiz bu yılı küçük ama anlamlı bir şekilde kutlamak için; etkisi, özverisi ve pozitif enerjisiyle
                biraz daha öne çıkan çalışma arkadaşımızı birlikte seçiyoruz.
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )


def show_result_hero():
    st.markdown(
        '''
        <div class="app-hero">
            <div class="hero-title">🏆 Our Employee of the Year</div>
            <div class="gold-line"></div>
            <div class="hero-subtitle">
                A special moment to celebrate the people who made a meaningful difference this year.<br><br>
                Bu yıl fark yaratan, katkısıyla öne çıkan çalışma arkadaşlarımızı gururla kutluyoruz.
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )


# =====================================================
# VOTE PAGE
# =====================================================

if menu == "Vote":
    show_vote_hero()

    st.header("🗳️ Vote / Oy Kullan")

    st.markdown(
        '''
        <div class="rule-wrapper">
            <div class="rule-card">
                <div class="rule-icon">🔒</div>
                <div class="rule-title">Confidential Voting</div>
                <div class="rule-text">Oy detayları sonuç ekranında gösterilmez.</div>
            </div>
            <div class="rule-card">
                <div class="rule-icon">🚫</div>
                <div class="rule-title">No Self-Voting</div>
                <div class="rule-text">Kendi adına oy veremezsin.</div>
            </div>
            <div class="rule-card">
                <div class="rule-icon">🏆</div>
                <div class="rule-title">Winner</div>
                <div class="rule-text">Finalde ilk 3 kişi açıklanır.</div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        '''
        <div class="section-card">
            <div class="section-card-title">Start Your Vote / Oy Vermeye Başla</div>
            <div class="section-card-subtitle">
                Please select your real name and write a nickname before answering the questions.<br>
                Soruları cevaplamadan önce gerçek ismini seç ve bir nickname yaz.
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    voter = st.selectbox(
        "1. Select your real name / Gerçek ismini seç",
        options=["Select / Seç"] + VOTERS
    )

    nickname = st.text_input(
        "2. Write your nickname / Nickname yaz",
        placeholder="Example: BlueTiger"
    )

    if voter == "Select / Seç":
        st.warning("Oy kullanmak için önce gerçek ismini seçmelisin.")
    elif has_voted(voter):
        st.error("Bu isim daha önce oy kullandı. Each real name can vote only once.")
    else:
        st.info("Kendi adına oy veremezsin. EDA oy kullanabilir ama oy verilecek kişiler listesinde yer almaz.")

        available_options = [person for person in EMPLOYEES if person != voter]

        answers = {}
        comments = {}

        with st.form("voting_form"):
            for question in QUESTIONS:
                st.markdown(
                    f'''
                    <div class="question-card">
                        <div class="question-title">Question {question["id"]} — {question["category"]}</div>
                        <div class="question-text"><b>EN:</b> {question["en"]}</div>
                        <div class="question-text"><b>TR:</b> {question["tr"]}</div>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )

                selected_person = st.radio(
                    "Choose one person / Bir kişi seç",
                    options=available_options,
                    key=f"question_{question['id']}",
                    horizontal=True,
                    index=None
                )

                comment = st.text_area(
                    "Why did you choose this person? / Bu kişiyi neden seçtin?",
                    placeholder="Kısa bir açıklama yaz...",
                    key=f"comment_{question['id']}"
                )

                answers[question["id"]] = selected_person
                comments[question["id"]] = comment.strip()

                st.divider()

            submitted = st.form_submit_button("Submit My Vote / Oyumu Gönder")

            if submitted:
                if not nickname.strip():
                    st.error("Lütfen nickname yaz.")
                elif any(value is None for value in answers.values()):
                    st.error("Lütfen tüm sorular için bir kişi seç.")
                elif any(comment == "" for comment in comments.values()):
                    st.error("Lütfen her soru için kısa bir açıklama yaz.")
                elif has_voted(voter):
                    st.error("Bu isim daha önce oy kullandı.")
                else:
                    save_votes(voter, nickname.strip(), answers, comments)
                    st.success("Oyun başarıyla kaydedildi. Thank you for voting!")
                    st.balloons()


# =====================================================
# FINAL RESULT PAGE
# =====================================================

elif menu == "Final Result":
    show_result_hero()

    st.header("🏆 Final Result / Final Sonuç")

    if "result_unlocked" not in st.session_state:
        st.session_state.result_unlocked = False

    if not st.session_state.result_unlocked:
        st.markdown(
            '''
            <div class="soft-card">
                <b>The final result is ready to be announced.</b><br>
                Final sonucu açıklamak için lütfen sonuç şifresini girin.
            </div>
            ''',
            unsafe_allow_html=True
        )

        result_password_input = st.text_input(
            "Result Password / Sonuç Şifresi",
            type="password",
            key="result_password_input"
        )

        if st.button("Reveal Top 3 / İlk 3'ü Açıkla"):
            if result_password_input == RESULT_PASSWORD:
                st.session_state.result_unlocked = True
                st.balloons()
                st.snow()
                st.rerun()
            else:
                st.error("Wrong password / Hatalı şifre")

    else:
        votes_df = load_votes()
        total_scores = calculate_total_scores(votes_df)

        if total_scores.empty:
            st.info("Henüz oy yok. No votes yet.")
        else:
            top_3_people = calculate_top_3_people_only(votes_df)

            st.balloons()
            st.snow()

            st.markdown(
                '''
                <div class="soft-card" style="text-align:center;">
                    <h2>✨ The Moment Has Come ✨</h2>
                    <p>
                        Every vote represents appreciation, respect and team spirit.<br>
                        Now it is time to reveal our Top 3!
                    </p>
                    <p>
                        Her oy; takdir, saygı ve ekip ruhunu temsil ediyor.<br>
                        Şimdi Top 3'ü açıklama zamanı!
                    </p>
                    <p>
                        <b>Each vote gives 10 points.</b><br>
                        <b>Her oy 10 puandır.</b>
                    </p>
                </div>
                ''',
                unsafe_allow_html=True
            )

            rank_icons = {
                1: "🏆",
                2: "🥈",
                3: "🥉"
            }

            rank_labels = {
                1: "1st Place / 1. Sıra",
                2: "2nd Place / 2. Sıra",
                3: "3rd Place / 3. Sıra"
            }

            for rank in [3, 2, 1]:
                rank_df = top_3_people[top_3_people["rank"] == rank]

                if not rank_df.empty:
                    names = ", ".join(rank_df["selected_person"].tolist())
                    score = int(rank_df["score"].iloc[0])
                    person_count = len(rank_df)

                    if person_count > 1:
                        tie_text = f"{person_count} people share this place / Bu sırayı {person_count} kişi paylaşıyor"
                    else:
                        tie_text = ""

                    if rank == 1:
                        st.markdown(
                            f'''
                            <div class="winner-box">
                                <div class="winner-label">{rank_icons[rank]} Employee of the Year / Yılın Elemanı {rank_icons[rank]}</div>
                                <div class="winner-name">{names}</div>
                                <div class="winner-score">Total Score / Toplam Puan: {score}</div>
                                <div class="winner-score" style="font-size:20px; margin-top:10px;">{tie_text}</div>
                            </div>
                            ''',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'''
                            <div class="top-three-box">
                                <div style="font-size:30px; font-weight:950;">{rank_icons[rank]} {rank_labels[rank]}</div>
                                <div style="font-size:48px; font-weight:950; margin:14px 0;">{names}</div>
                                <div style="font-size:25px; font-weight:850;">Total Score / Toplam Puan: {score}</div>
                                <div style="font-size:18px; font-weight:750; margin-top:10px;">{tie_text}</div>
                            </div>
                            ''',
                            unsafe_allow_html=True
                        )

            st.markdown(
                '''
                <div class="soft-card" style="text-align:center; margin-top:24px;">
                    <b>Congratulations to our Top 3!</b><br>
                    This result is a celebration of contribution, support and team spirit.<br><br>
                    <b>Top 3'ümüzü tebrik ederiz!</b><br>
                    Bu sonuç; katkının, desteğin ve ekip ruhunun bir kutlamasıdır.
                </div>
                ''',
                unsafe_allow_html=True
            )

            if st.button("Hide Result / Sonucu Gizle"):
                st.session_state.result_unlocked = False
                st.rerun()


# =====================================================
# ADMIN PAGE
# =====================================================

elif menu == "Admin":
    show_result_hero()

    st.header("🔐 Admin Panel")

    password = st.text_input("Admin password", type="password")

    if password == ADMIN_PASSWORD or password == FULL_ADMIN_PASSWORD:
        votes_df = load_votes()

        is_full_admin = password == FULL_ADMIN_PASSWORD

        if is_full_admin:
            st.success("Full admin access granted. Raw voting details are visible.")
        else:
            st.success("Limited admin access granted. Voter and nickname details are hidden.")

        if votes_df.empty:
            st.info("Henüz oy yok.")
        else:
            total_voters = votes_df["voter"].nunique()
            total_votes = len(votes_df)
            total_points = votes_df["score"].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Voters", total_voters)
            col2.metric("Total Votes", total_votes)
            col3.metric("Total Points", total_points)

            st.divider()

            st.subheader("Top 3 Result")
            top_3_people = calculate_top_3_people_only(votes_df)

            rank_icons = {
                1: "🏆",
                2: "🥈",
                3: "🥉"
            }

            rank_labels = {
                1: "1st Place",
                2: "2nd Place",
                3: "3rd Place"
            }

            for rank in [1, 2, 3]:
                rank_df = top_3_people[top_3_people["rank"] == rank]

                if not rank_df.empty:
                    names = ", ".join(rank_df["selected_person"].tolist())
                    score = int(rank_df["score"].iloc[0])

                    st.markdown(f"### {rank_icons[rank]} {rank_labels[rank]}: {names}")
                    st.metric("Score", score)

            st.divider()

            st.subheader("Total Scores")
            total_scores = calculate_total_scores(votes_df)
            st.dataframe(total_scores, use_container_width=True)
            st.bar_chart(total_scores.set_index("selected_person"))

            st.divider()

            st.subheader("Category Winners")
            category_winners = calculate_category_winners(votes_df)
            st.dataframe(category_winners, use_container_width=True)

            st.divider()

            st.subheader("Vote Details")

            if is_full_admin:
                st.warning("Full view: Bu tablo kim kime oy verdi bilgisini içerir.")
                st.dataframe(votes_df, use_container_width=True)

                csv = votes_df.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label="Download Full Votes as CSV",
                    data=csv,
                    file_name="employee_of_the_year_votes_full.csv",
                    mime="text/csv"
                )

            else:
                st.info("Limited view: Voter ve nickname bilgileri gizlenmiştir.")

                anonymous_votes_df = votes_df.drop(
                    columns=["voter", "nickname"],
                    errors="ignore"
                )

                st.dataframe(anonymous_votes_df, use_container_width=True)

                csv = anonymous_votes_df.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label="Download Anonymous Votes as CSV",
                    data=csv,
                    file_name="employee_of_the_year_votes_anonymous.csv",
                    mime="text/csv"
                )

            st.divider()

            with st.expander("Danger Zone"):
                st.warning("Bu işlem tüm oyları siler.")

                if is_full_admin:
                    confirm_reset = st.checkbox("I understand. Delete all votes.")
                    if st.button("Reset All Votes"):
                        if confirm_reset:
                            reset_votes()
                            st.success("Tüm oylar silindi. Sayfayı yenileyebilirsin.")
                        else:
                            st.error("Silmek için onay kutusunu işaretlemelisin.")
                else:
                    st.error("Reset işlemi sadece full admin şifresi ile yapılabilir.")

    elif password:
        st.error("Wrong password.")
    else:
        st.info("Admin sonuçlarını görmek için şifre gir.")
