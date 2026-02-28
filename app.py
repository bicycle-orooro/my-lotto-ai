import pandas as pd
import streamlit as st
import random
import os

CSV_FILE = "lotto_data.csv"

# ==========================================
# 🎨 스마트폰 화면 비율 강제 적용 (Custom CSS)
# ==========================================
def apply_mobile_layout():
    st.markdown(
        """
        <style>
        /* 1. 전체 화면의 최대 너비를 스마트폰 크기(450px)로 제한하고 가운데 정렬 */
        .block-container {
            max-width: 450px !important;
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }
        
        /* 2. 좁아진 화면에 6개가 예쁘게 들어가도록 로또 공 크기 미세 조정 */
        .lotto-ball {
            display: inline-block;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            text-align: center;
            line-height: 40px;
            font-size: 16px;
            font-weight: bold;
            margin-right: 6px;
            margin-bottom: 10px;
            box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        /* 3. 상단 헤더 숨기기 (더 앱처럼 보이게) */
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )

def get_lotto_ball_html(number):
    if number <= 10:
        bg_color = "#fbc400"; text_color = "black"
    elif number <= 20:
        bg_color = "#69c8f2"; text_color = "black"
    elif number <= 30:
        bg_color = "#ff7272"; text_color = "white"
    elif number <= 40:
        bg_color = "#aaaaaa"; text_color = "white"
    else:
        bg_color = "#b0d840"; text_color = "black"
        
    # 위에서 정의한 .lotto-ball CSS 클래스를 적용합니다.
    return f'<div class="lotto-ball" style="background-color: {bg_color}; color: {text_color};">{number}</div>'

# ==========================================
# 📊 데이터 로드
# ==========================================
def load_data():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()
    try:
        df = pd.read_csv(CSV_FILE, header=None, names=['draw_no', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6'])
        df = df.apply(pd.to_numeric, errors='coerce').dropna().astype(int)
        return df
    except:
        return pd.DataFrame()

# ==========================================
# 🤖 AI 기반 번호 예측 알고리즘
# ==========================================
def generate_ai_numbers(df, num_sets=3):
    if df.empty:
        return [[1, 2, 3, 4, 5, 6] for _ in range(num_sets)]
        
    all_nums = df[['num1', 'num2', 'num3', 'num4', 'num5', 'num6']].values.flatten()
    recent_nums = df.head(10)[['num1', 'num2', 'num3', 'num4', 'num5', 'num6']].values.flatten()
    
    all_counts = pd.Series(all_nums).value_counts()
    recent_counts = pd.Series(recent_nums).value_counts()
    
    weights = {i: 1.0 for i in range(1, 46)}
    
    for num in range(1, 46):
        if num in all_counts:
            weights[num] += all_counts[num] * 0.02
        if num in recent_counts:
            weights[num] += recent_counts[num] * 0.5
            
    weight_list = [weights[i] for i in range(1, 46)]
    
    generated_sets = []
    for _ in range(num_sets):
        selected = []
        while len(selected) < 6:
            pick = random.choices(range(1, 46), weights=weight_list, k=1)[0]
            if pick not in selected:
                selected.append(pick)
        selected.sort() 
        generated_sets.append(selected)
        
    return generated_sets

# ==========================================
# 🖥️ 웹 UI 구성 (Streamlit)
# ==========================================
st.set_page_config(page_title="AI 로또 예측기", page_icon="🤖")

# 🚀 모바일 전용 레이아웃 강제 적용!
apply_mobile_layout()

st.title("🤖 AI 로또 예측 앱")
st.write("빅데이터 트렌드 가중치를 분석하여 추천합니다.")

df = load_data()

if not df.empty:
    latest_draw = df['draw_no'].iloc[0]
    st.info(f"✅ **{latest_draw}회차**까지 과거 데이터 학습 완료!")
    
    # AI 번호 추출 버튼
    if st.button("✨ AI 번호 3세트 생성하기", type="primary", use_container_width=True):
        with st.spinner('확률을 계산 중입니다...'):
            ai_sets = generate_ai_numbers(df, num_sets=3)
            
            st.subheader("🎯 AI 추천 번호")
            
            for i, num_set in enumerate(ai_sets):
                st.caption(f"**추천 세트 {i+1}**")
                balls_html = "".join([get_lotto_ball_html(num) for num in num_set])
                st.markdown(f'<div style="margin-bottom: 15px;">{balls_html}</div>', unsafe_allow_html=True)

    st.write("---")
    
    with st.expander("📊 과거 당첨 번호 데이터베이스"):
        st.dataframe(df, use_container_width=True)
else:
    st.error("데이터 파일을 찾을 수 없습니다.")