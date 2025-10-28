import streamlit as st
import pandas as pd
import altair as alt

# --------------------------
# 📘 기본 설정
# --------------------------
st.set_page_config(page_title="MBTI 유형별 국가 TOP 10", layout="wide")

st.title("🌍 MBTI 유형별 국가 TOP 10 분석 대시보드")
st.caption("CSV: countriesMBTI_16types.csv — 특정 MBTI 유형이 많은 나라를 찾아보세요!")

# --------------------------
# 📂 데이터 불러오기
# --------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    # 컬럼명 표준화
    df.columns = [c.strip() for c in df.columns]
    return df

df = load_data()

# --------------------------
# 📊 MBTI 타입 컬럼 탐지
# --------------------------
mbti_cols = [c for c in df.columns if len(c) == 4 and c.isalpha()]
country_col = next((c for c in df.columns if "country" in c.lower()), df.columns[0])

# --------------------------
# 🎛️ 사용자 선택 영역
# --------------------------
st.sidebar.header("⚙️ 설정")
selected_type = st.sidebar.selectbox("분석할 MBTI 유형을 선택하세요", sorted(mbti_cols))
top_n = st.sidebar.slider("표시할 국가 수", 5, 20, 10)

# --------------------------
# 🔍 데이터 처리
# --------------------------
df_selected = df[[country_col, selected_type]].copy()
df_selected = df_selected.sort_values(by=selected_type, ascending=False).head(top_n)

# --------------------------
# 📈 Altair 시각화
# --------------------------
chart = (
    alt.Chart(df_selected)
    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
    .encode(
        x=alt.X(f"{selected_type}:Q", title=f"{selected_type} 비율 / 인원수"),
        y=alt.Y(f"{country_col}:N", sort='-x', title="국가"),
        color=alt.Color(f"{selected_type}:Q", scale=alt.Scale(scheme="tealblues")),
        tooltip=[country_col, selected_type],
    )
    .properties(height=500, title=f"🌟 {selected_type} 유형이 높은 국가 TOP {top_n}")
    .configure_axis(grid=False)
    .configure_view(strokeWidth=0)
)

st.altair_chart(chart, use_container_width=True)

# --------------------------
# 📋 데이터 테이블 표시
# --------------------------
with st.expander("📄 데이터 미리보기"):
    st.dataframe(df_selected.reset_index(drop=True), use_container_width=True)

# --------------------------
# 💡 인사이트 요약
# --------------------------
top_country = df_selected.iloc[0][country_col]
top_value = df_selected.iloc[0][selected_type]

st.markdown(
    f"""
    ### ✨ 인사이트  
    - **가장 높은 {selected_type} 비율**을 보인 국가는 **{top_country}**, 값은 **{top_value:,}** 입니다.  
    - 상위 {top_n}개국의 {selected_type} 분포를 한눈에 비교할 수 있습니다.  
    - 사이드바에서 MBTI 유형이나 표시 국가 수를 바꿔보세요!
    """
)
