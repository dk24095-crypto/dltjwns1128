import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="MBTI 유형별 국가 TOP 10", layout="wide")
st.title("🌍 MBTI 유형별 국가 TOP 10 분석 대시보드")

# 🔹 CSV 업로드
uploaded_file = st.file_uploader("📂 MBTI 데이터 파일을 업로드하세요 (countriesMBTI_16types.csv)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ 파일이 성공적으로 업로드되었습니다.")
    
    # 컬럼 정리
    df.columns = [c.strip() for c in df.columns]
    mbti_cols = [c for c in df.columns if len(c) == 4 and c.isalpha()]
    country_col = next((c for c in df.columns if "country" in c.lower()), df.columns[0])

    # 사용자 선택
    st.sidebar.header("⚙️ 설정")
    selected_type = st.sidebar.selectbox("분석할 MBTI 유형을 선택하세요", sorted(mbti_cols))
    top_n = st.sidebar.slider("표시할 국가 수", 5, 20, 10)

    df_selected = df[[country_col, selected_type]].sort_values(by=selected_type, ascending=False).head(top_n)

    # Altair 차트
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

    with st.expander("📄 데이터 미리보기"):
        st.dataframe(df_selected, use_container_width=True)

else:
    st.info("⬆️ 먼저 CSV 파일을 업로드하세요. (예: countriesMBTI_16types.csv)")

