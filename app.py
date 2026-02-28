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
        .block-container {
            max-width: 450px !important;
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }
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
    return f'<div class="lotto-ball" style="background-color: {bg_color}; color: {text_color};">{number}</div>'

# ==========================================
# 📊 데이터 로드 (캐싱으로 속도 향상)
# ==========================================
@st.cache_data
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
# 🤖 AI 기반 번호 예측 알고리즘 (+ 고정수/제외수)
# ==========================================
def generate_ai_numbers(df, num_sets=5, fixed_nums=[], excluded_nums=[]):
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
            
        # ⚠️ 핵심 기능: 사용자가 입력한 고정수와 제외수 통제
        if num in excluded_nums:
            weights[num] = 0.0  # 제외수는 가중치를 0으로 만들어 절대 뽑히지 않게 함
        if num in fixed_nums:
            weights[num] = 0.0  # 고정수는 이미 뽑힌 것으로 간주하여 중복 추출 방지

    weight_list = [weights[i] for i in range(1, 46)]
    
    generated_sets = []
    for _ in range(num_sets):
        selected = fixed_nums.copy() # 고정수를 먼저 바구니에 담고 시작
        
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
st.set_page_config(page_title="AI 로또 예측기", page_icon="🎲")
apply_mobile_layout()

st.title("🎲 AI 로또 예측 앱")
st.write("빅데이터 통계와 나의 직감을 조합해 보세요!")

df = load_data()

if not df.empty:
    latest_draw = df['draw_no'].iloc[0]
    st.info(f"✅ **{latest_draw}회차**까지 과거 데이터 학습 완료")
    
    # 🎯 1. 고정수 / 제외수 지정 기능 (토글로 접었다 폈다 할 수 있게 만듦)
    with st.expander("🛠️ 나만의 번호 설정 (고정수/제외수)"):
        all_numbers = list(range(1, 46))
        
        fixed_nums = st.multiselect("📌 무조건 포함할 번호 (고정수, 최대 5개)", all_numbers, max_selections=5)
        excluded_nums = st.multiselect("❌ 절대 안 나올 번호 (제외수)", all_numbers)
        
        # 에러 방지: 고정수와 제외수에 같은 번호를 넣는 실수 방지
        intersect = set(fixed_nums) & set(excluded_nums)
        if intersect:
            st.error(f"⚠️ 고정수와 제외수에 같은 번호({', '.join(map(str, intersect))})가 있습니다! 하나는 빼주세요.")

    # 🎯 2. AI 번호 추출 버튼 (5세트로 변경)
    if st.button("✨ AI 번호 5세트 생성하기", type="primary", use_container_width=True):
        if intersect:
            st.warning("고정수와 제외수 충돌을 먼저 해결해 주세요!")
        else:
            with st.spinner('최적의 조합을 계산 중입니다...'):
                ai_sets = generate_ai_numbers(df, num_sets=5, fixed_nums=fixed_nums, excluded_nums=excluded_nums)
                
                st.subheader("🎯 AI 추천 번호")
                
                # 🎯 3. 공유하기용 텍스트 생성 준비
                share_text = f"🤖 AI 로또 추천 번호 ({latest_draw}회차)\n\n"
                
                for i, num_set in enumerate(ai_sets):
                    st.caption(f"**추천 세트 {i+1}**")
                    balls_html = "".join([get_lotto_ball_html(num) for num in num_set])
                    st.markdown(f'<div style="margin-bottom: 15px;">{balls_html}</div>', unsafe_allow_html=True)
                    
                    # 공유하기 텍스트에 한 줄씩 추가
                    share_text += f"세트 {i+1} : {', '.join(map(str, num_set))}\n"
                
                # 안내 문구 (여기에 나중에 발급받은 Streamlit URL을 넣으시면 됩니다)
                share_text += "\n지금 무료로 나만의 AI 번호를 뽑아보세요!\n👉 https://[나의-스트림릿-주소].streamlit.app"
                
                st.write("---")
                
                # 🎯 4. 카카오톡 공유하기 박스 (우측 상단 복사 아이콘 제공)
                st.write("📲 **번호 공유하기 (복사해서 붙여넣기)**")
                st.caption("아래 박스 오른쪽 위의 📋(복사) 버튼을 눌러 카카오톡에 바로 붙여넣어 보세요!")
                st.code(share_text, language="text")

    st.write("---")
    
    with st.expander("📊 과거 당첨 번호 데이터베이스"):
        st.dataframe(df, use_container_width=True)
else:
    st.error("데이터 파일을 찾을 수 없습니다.")
