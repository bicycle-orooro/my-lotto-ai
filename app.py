import pandas as pd
import streamlit as st
import random
import os
import pathlib # 🎯 파일 경로를 찾기 위한 모듈 추가

CSV_FILE = "lotto_data.csv"

# ==========================================
# 📈 구글 애널리틱스 (코어 HTML 직접 수정 기법)
# ==========================================
def inject_ga(tracking_id):
    if tracking_id == "G-XXXXXXXXXX":
        return
        
    # 1. 스트림릿 서버 깊숙한 곳에 있는 진짜 'index.html' 파일의 위치를 찾아냅니다.
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    
    # 2. 원본 파일을 읽어옵니다.
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    # 3. 만약 내 G-코드가 아직 안 심어져 있다면 (서버가 처음 켜졌을 때만 작동)
    if tracking_id not in html_content:
        ga_script = f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={tracking_id}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', '{tracking_id}');
        </script>
        """
        # 4. 원본 HTML의 <head> 태그 바로 밑에 구글 코드를 강제로 욱여넣습니다.
        new_html = html_content.replace("<head>", f"<head>\n{ga_script}")
        
        # 5. 수정한 내용으로 원본 파일을 완전히 덮어씁니다!
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(new_html)

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
            
        if num in excluded_nums:
            weights[num] = 0.0  
        if num in fixed_nums:
            weights[num] = 0.0  

    weight_list = [weights[i] for i in range(1, 46)]
    
    generated_sets = []
    for _ in range(num_sets):
        selected = fixed_nums.copy() 
        
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

# 🚀 기존 코드를 지우고, 새로 만든 해킹 함수로 변경합니다!
inject_ga("G-X29DQR6BSL")

apply_mobile_layout()

st.title("🎲 AI 로또 예측 앱")
st.write("빅데이터 통계와 나의 직감을 조합해 보세요!")

df = load_data()

if not df.empty:
    latest_draw = df['draw_no'].iloc[0]
    next_draw = latest_draw + 1 # 🎯 핵심: 다음 회차 계산
    
    st.info(f"✅ **{latest_draw}회차** 데이터 학습 완료 (다음 추첨: **{next_draw}회차**)")
    
    with st.expander("🛠️ 나만의 번호 설정 (고정수/제외수)"):
        all_numbers = list(range(1, 46))
        
        fixed_nums = st.multiselect("📌 무조건 포함할 번호 (고정수, 최대 5개)", all_numbers, max_selections=5)
        excluded_nums = st.multiselect("❌ 절대 안 나올 번호 (제외수)", all_numbers)
        
        intersect = set(fixed_nums) & set(excluded_nums)
        if intersect:
            st.error(f"⚠️ 고정수와 제외수에 같은 번호({', '.join(map(str, intersect))})가 있습니다! 하나는 빼주세요.")

    if st.button("✨ AI 번호 5세트 생성하기", type="primary", use_container_width=True):
        if intersect:
            st.warning("고정수와 제외수 충돌을 먼저 해결해 주세요!")
        else:
            with st.spinner('최적의 조합을 계산 중입니다...'):
                ai_sets = generate_ai_numbers(df, num_sets=5, fixed_nums=fixed_nums, excluded_nums=excluded_nums)
                
                st.subheader("🎯 AI 추천 번호")
                
                # 🎯 핵심: 공유하기 텍스트에 +1 된 다음 회차 반영!
                share_text = f"🤖 AI 로또 추천 번호 ({next_draw}회차)\n\n"
                
                for i, num_set in enumerate(ai_sets):
                    st.caption(f"**추천 세트 {i+1}**")
                    balls_html = "".join([get_lotto_ball_html(num) for num in num_set])
                    st.markdown(f'<div style="margin-bottom: 15px;">{balls_html}</div>', unsafe_allow_html=True)
                    
                    share_text += f"세트 {i+1} : {', '.join(map(str, num_set))}\n"
                
                # ⚠️ 아래 주소를 본인이 스트림릿에서 발급받은 실제 주소로 바꿔주세요!
                share_text += "\n지금 무료로 나만의 AI 번호를 뽑아보세요!\n👉 https://lotto-ai-pro.streamlit.app"
                
                st.write("---")
                st.write("📲 **번호 공유하기 (복사해서 붙여넣기)**")
                st.caption("아래 박스 오른쪽 위의 📋(복사) 버튼을 눌러 카카오톡에 바로 붙여넣어 보세요!")
                st.code(share_text, language="text")

    st.write("---")
    
    with st.expander("📊 과거 당첨 번호 데이터베이스"):
        st.dataframe(df, use_container_width=True)
else:
    st.error("데이터 파일을 찾을 수 없습니다.")
