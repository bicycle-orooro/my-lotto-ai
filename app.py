import pandas as pd
import streamlit as st
import random
import os
import streamlit.components.v1 as components 
import altair as alt # 🎯 줌(Zoom) 방지를 위한 고급 차트 라이브러리 추가!

CSV_FILE = "lotto_data.csv"

# ==========================================
# 0. 페이지 기본 설정
# ==========================================
st.set_page_config(page_title="AI 로또 예측기 | 무료 번호 추천", page_icon="🎲")

# ==========================================
# 📈 구글 애널리틱스 
# ==========================================
def inject_ga(tracking_id):
    if tracking_id == "G-XXXXXXXXXX":
        return
        
    ga_js = f"""
    <script>
        var parentDoc = window.parent.document;
        if (!parentDoc.getElementById("ga-script")) {{
            var gaScript = parentDoc.createElement("script");
            gaScript.id = "ga-script";
            gaScript.async = true;
            gaScript.src = "https://www.googletagmanager.com/gtag/js?id={tracking_id}";
            parentDoc.head.appendChild(gaScript);

            var gaInline = parentDoc.createElement("script");
            gaInline.innerHTML = `
                window.dataLayer = window.dataLayer || [];
                function gtag(){{dataLayer.push(arguments);}}
                gtag('js', new Date());
                gtag('config', '{tracking_id}');
            `;
            parentDoc.head.appendChild(gaInline);
        }}
    </script>
    """
    components.html(ga_js, width=0, height=0)

# ==========================================
# 🎨 스마트폰 앱 느낌 UI/UX 최적화 (Custom CSS)
# ==========================================
def apply_mobile_layout():
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 450px !important;
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
        }
        
        h1 { font-size: 22px !important; font-weight: 800 !important; }
        h2 { font-size: 18px !important; font-weight: 700 !important; }
        h3 { font-size: 15px !important; font-weight: 600 !important; opacity: 0.8; }
        
        .lotto-ball {
            display: inline-block;
            width: 36px;       
            height: 36px;
            border-radius: 50%;
            text-align: center;
            line-height: 36px;
            font-size: 14px;   
            font-weight: bold;
            margin-right: 4px; 
            margin-bottom: 5px;
            box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        [data-testid="stMetricValue"] {
            font-size: 20px !important; 
            font-weight: 700 !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 12px !important; 
        }
        
        .stButton>button {
            border-radius: 10px;
            font-weight: bold;
            font-size: 16px;
            padding: 10px;
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
# 📊 데이터 로드
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
# 🤖 AI 기반 예측 알고리즘
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
        if num in all_counts: weights[num] += all_counts[num] * 0.02
        if num in recent_counts: weights[num] += recent_counts[num] * 0.5
        if num in excluded_nums: weights[num] = 0.0  
        if num in fixed_nums: weights[num] = 0.0  

    weight_list = [weights[i] for i in range(1, 46)]
    generated_sets = []
    for _ in range(num_sets):
        selected = fixed_nums.copy() 
        while len(selected) < 6:
            pick = random.choices(range(1, 46), weights=weight_list, k=1)[0]
            if pick not in selected: selected.append(pick)
        selected.sort() 
        generated_sets.append(selected)
        
    return generated_sets

# ==========================================
# 📊 통계 분석 풀세트 
# ==========================================
def show_statistics_dashboard(df):

    st.header("📊 로또 데이터 분석 리포트")

    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    recent = df.head(10)
    all_nums = recent[['num1','num2','num3','num4','num5','num6']].values.flatten()
    counts = pd.Series(all_nums).value_counts().sort_index()

    with st.container(border=True):
        st.subheader("🔥 최근 10회 핫번호 TOP 5")
        hot = counts.sort_values(ascending=False).head(5)
        hot_html = "".join([f"<div style='display:inline-block; text-align:center; margin-right:8px;'>{get_lotto_ball_html(num)}<br><span style='font-size:11px; opacity:0.6;'>{hot[num]}회</span></div>" for num in hot.index])
        st.markdown(hot_html, unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("❄️ 최근 10회 미출현 번호")
        missing = [n for n in range(1,46) if n not in counts.index]
        missing_html = "".join([get_lotto_ball_html(num) for num in missing[:7]])
        st.markdown(missing_html, unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("⚖️ 홀짝 비율 & ➕ 합계 평균")
        even = sum(n % 2 == 0 for n in all_nums)
        odd = sum(n % 2 == 1 for n in all_nums)
        sums = recent[['num1','num2','num3','num4','num5','num6']].sum(axis=1)

        odd_rate = round((odd/60)*100)
        even_rate = round((even/60)*100)
        avg_sum = round(sums.mean(), 1)

        metrics_html = f"""
        <div style="display: flex; justify-content: space-between; text-align: center; padding: 5px 0;">
            <div style="flex: 1;">
                <div style="font-size: 12px; opacity: 0.7; margin-bottom: 4px;">홀수 비율</div>
                <div style="font-size: 20px; font-weight: 700;">{odd_rate}%</div>
            </div>
            <div style="flex: 1; border-left: 1px solid rgba(128,128,128,0.2); border-right: 1px solid rgba(128,128,128,0.2);">
                <div style="font-size: 12px; opacity: 0.7; margin-bottom: 4px;">짝수 비율</div>
                <div style="font-size: 20px; font-weight: 700;">{even_rate}%</div>
            </div>
            <div style="flex: 1;">
                <div style="font-size: 12px; opacity: 0.7; margin-bottom: 4px;">평균 합계</div>
                <div style="font-size: 20px; font-weight: 700;">{avg_sum}</div>
            </div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)

    # 🎯 수정 1: 구간별 분포 차트를 Altair로 변경 (줌/스크롤 방지)
    with st.container(border=True):
        st.subheader("📈 구간별 출현 분포")
        bins = {"1~10": 0, "11~20": 0, "21~30": 0, "31~40": 0, "41~45": 0}
        for n in all_nums:
            if n <= 10: bins["1~10"] += 1
            elif n <= 20: bins["11~20"] += 1
            elif n <= 30: bins["21~30"] += 1
            elif n <= 40: bins["31~40"] += 1
            else: bins["41~45"] += 1
            
        df_bins = pd.DataFrame({"구간": list(bins.keys()), "출현 횟수": list(bins.values())})
        bar_chart = alt.Chart(df_bins).mark_bar(color='#ff7272', cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X('구간', sort=None, title=None),
            y=alt.Y('출현 횟수', title=None),
            tooltip=['구간', '출현 횟수']
        ).properties(height=200)
        st.altair_chart(bar_chart, use_container_width=True) # 기본적으로 확대/축소 불가능!

    # 🎯 수정 2: 합계 라인 차트도 Altair로 변경 (가로축에 정확한 회차 이름 표시 보너스!)
    with st.container(border=True):
        st.subheader("➕ 최근 10회 합계 흐름")
        
        # 최근 10회차를 시간순(과거->현재)으로 정렬하여 차트 데이터 생성
        df_sums = pd.DataFrame({
            "회차": recent['draw_no'].astype(str) + "회",
            "합계": sums.values
        }).iloc[::-1] 
        
        line_chart = alt.Chart(df_sums).mark_line(color='#69c8f2', point=True).encode(
            x=alt.X('회차', sort=None, title=None),
            y=alt.Y('합계', scale=alt.Scale(zero=False), title=None),
            tooltip=['회차', '합계']
        ).properties(height=200)
        st.altair_chart(line_chart, use_container_width=True)

    with st.container(border=True):
        st.subheader("🎯 연속번호 및 AI 신뢰도")
        consecutive_count = 0
        for _, row in recent.iterrows():
            nums = sorted(row[['num1','num2','num3','num4','num5','num6']])
            for i in range(5):
                if nums[i] + 1 == nums[i+1]:
                    consecutive_count += 1
                    break

        rate = (consecutive_count / len(recent)) * 100
        confidence = min(90, 50 + int(rate / 2) + len(hot))
        
        st.metric("10회 연속번호 출현", f"{round(rate,1)}%")
        st.progress(confidence / 100)
        st.caption(f"통계 가중치 기반 AI 분석 신뢰도 {confidence}%")

# ==========================================
# 🖥️ 메인 웹 화면 구성
# ==========================================
inject_ga("G-X29DQR6BSL")

apply_mobile_layout()

with st.container(border=True):
    st.title("🎲 AI 로또 예측 앱")
    st.write("빅데이터 통계와 나의 직감을 조합해 보세요!")

df = load_data()

if not df.empty:
    latest_draw = df['draw_no'].iloc[0]
    next_draw = latest_draw + 1 
    
    st.info(f"✅ **{latest_draw}회차** 데이터 학습 완료 (다음: **{next_draw}회차**)")
    
    with st.container(border=True):
        with st.expander("🛠️ 나만의 번호 설정 (고정수/제외수)"):
            all_numbers = list(range(1, 46))
            fixed_nums = st.multiselect("📌 무조건 포함할 번호 (최대 5개)", all_numbers, max_selections=5)
            excluded_nums = st.multiselect("❌ 절대 안 나올 번호", all_numbers)
            
            intersect = set(fixed_nums) & set(excluded_nums)
            if intersect:
                st.error(f"⚠️ 중복 번호가 있습니다: {', '.join(map(str, intersect))}")

    if st.button("✨ AI 번호 5세트 생성하기", type="primary", use_container_width=True):
        if intersect:
            st.warning("고정수와 제외수 충돌을 먼저 해결해 주세요!")
        else:
            with st.spinner('최적의 조합을 계산 중입니다...'):
                ai_sets = generate_ai_numbers(df, num_sets=5, fixed_nums=fixed_nums, excluded_nums=excluded_nums)
                
                with st.container(border=True):
                    st.subheader("🎯 AI 추천 번호")
                    share_text = f"🤖 AI 로또 추천 번호 ({next_draw}회차)\n\n"
                    
                    for i, num_set in enumerate(ai_sets):
                        st.caption(f"**추천 세트 {i+1}**")
                        balls_html = "".join([get_lotto_ball_html(num) for num in num_set])
                        st.markdown(f'<div style="margin-bottom: 12px;">{balls_html}</div>', unsafe_allow_html=True)
                        share_text += f"세트 {i+1} : {', '.join(map(str, num_set))}\n"
                    
                    share_text += "\n무료로 나만의 AI 번호 뽑기!\n👉 https://bicycle-orooro.github.io/my-lotto-ai/"
                    
                    st.write("---")
                    st.write("📲 **번호 공유하기**")
                    st.code(share_text, language="text")

    st.write("---")
    
    show_statistics_dashboard(df)
    
    with st.expander("📊 과거 당첨 번호 데이터베이스 확인"):
        st.dataframe(df, use_container_width=True)
else:
    st.error("데이터 파일을 찾을 수 없습니다.")
