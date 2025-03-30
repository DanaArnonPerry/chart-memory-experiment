import streamlit as st
import pandas as pd
import os
import random
from PIL import Image

st.set_page_config(layout="wide", page_title="ניסוי זיכרון חזותי")
st.markdown("<style>body {direction: rtl; text-align: right;}</style>", unsafe_allow_html=True)

def load_data():
    df = pd.read_csv("MemoryTest.csv", encoding='utf-8-sig')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.dropna(subset=['ChartNumber', 'Condition'], inplace=True)
    df['full_image_path'] = df['ImageFileName'].apply(lambda x: os.path.join("images", os.path.basename(x.strip())) if pd.notna(x) else '')
    return df

def show_question(question, options, key):
    st.markdown(f"<p style='direction: rtl; text-align: right; font-size:18px;'><strong>{question}</strong></p>", unsafe_allow_html=True)
    return st.radio("", options, key=key, format_func=lambda x: f"{chr(65 + options.index(x))}. {x}", label_visibility="collapsed")

def show_confidence(key):
    st.markdown(f"<p style='direction: rtl; text-align: right; font-size:16px;'>באיזו מידה אתה בטוח בתשובתך? (0-100)</p>", unsafe_allow_html=True)
    return st.slider("", 0, 100, 50, 10, key=key, label_visibility="collapsed")

df = load_data()

if "stage" not in st.session_state:
    st.session_state.stage = 0
    st.session_state.chosen = random.sample(df['ChartNumber'].unique().tolist(), 10)
    st.session_state.responses = []

chart_idx = st.session_state.stage

if chart_idx < len(st.session_state.chosen):
    chart = st.session_state.chosen[chart_idx]
    condition = random.choice(df[df['ChartNumber'] == chart]['Condition'].dropna().unique().tolist())
    row = df[(df['ChartNumber'] == chart) & (df['Condition'] == condition)].iloc[0]

    st.markdown(f"<h4 style='direction: rtl; text-align: right;'>גרף מספר: {row['ChartNumber']} | תנאי: {row['Condition']}</h4>", unsafe_allow_html=True)
    st.markdown(f"<p style='direction: rtl; text-align: right;'><strong>{row['Title']}</strong></p>", unsafe_allow_html=True)

    image_path = row['full_image_path']
    if os.path.exists(image_path):
        st.image(Image.open(image_path), use_container_width=True)
    else:
        st.warning(f"תמונה לא נמצאה: {image_path}")

    with st.form(key=f"form_{chart_idx}"):
        st.markdown("<h3 style='direction: rtl; text-align: right;'>שאלה 1</h3>", unsafe_allow_html=True)
        answer1 = show_question(row['Question1Text'], [row['OptionA'], row['OptionB'], row['OptionC'], row['OptionD']], f"q1_{chart_idx}")
        confidence1 = show_confidence(f"conf1_{chart_idx}")

        st.markdown("<h3 style='direction: rtl; text-align: right;'>שאלה 2</h3>", unsafe_allow_html=True)
        answer2 = show_question(row['Question2Text'], [row['OptionA.1'], row['OptionB.1'], row['OptionC.1'], row['OptionD.1']], f"q2_{chart_idx}")
        confidence2 = show_confidence(f"conf2_{chart_idx}")

        st.markdown("<h3 style='direction: rtl; text-align: right;'>שאלה 3</h3>", unsafe_allow_html=True)
        answer3 = show_question(row['Question3Text'], [row['OptionA.2'], row['OptionB.2'], row['OptionC.2'], row['OptionD.2']], f"q3_{chart_idx}")
        confidence3 = show_confidence(f"conf3_{chart_idx}")

        submit = st.form_submit_button("המשך")
        if submit:
            st.session_state.responses.append({
                'ChartNumber': row['ChartNumber'],
                'Condition': row['Condition'],
                'answer1': answer1, 'confidence1': confidence1,
                'answer2': answer2, 'confidence2': confidence2,
                'answer3': answer3, 'confidence3': confidence3,
            })
            st.session_state.stage += 1
            st.experimental_rerun()

else:
    st.success("הניסוי הסתיים! תודה על השתתפותך.")
    df_out = pd.DataFrame(st.session_state.responses)
    st.dataframe(df_out)
    st.download_button("הורד תוצאות כקובץ CSV", df_out.to_csv(index=False), "results.csv", "text/csv")
