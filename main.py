import streamlit as st
import pandas as pd
import altair as alt

# --------------------------------------
# 🎯 기본 설정
# --------------------------------------
st.set_page_config(page_title="국민연금 투자 분석", layout="wide")

st.title("💹 국민연금 국내주식 투자 분석")
st.markdown("""
이 앱은 **국민연금공단의 국내주식 투자 데이터**를 바탕으로  
`평가액(억 원)`과 `지분율(퍼센트)`의 관계를 시각적으로 분석합니다.
""")

# --------------------------------------
# 📂 CSV 업로드
# --------------------------------------
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    try:
        # 한국어 CSV는 CP949 인코딩으로 읽기
        df = pd.read_csv(uploaded_file, encoding="cp949")
    except:
        # 혹시 모를 UTF-8 BOM 대응
        df = pd.read_csv(uploaded_file, encoding="utf-8-sig")

    # --------------------------------------
    # 📋 데이터 미리보기
    # --------------------------------------
    st.subheader("데이터 미리보기")
    st.dataframe(df.head())

    # 컬럼명 자동 인식
    cols = df.columns
    st.markdown(f"**컬럼명:** {', '.join(cols)}")

    # 숫자형 컬럼만 골라 타입 변환 시도
    df["평가액(억 원)"] = pd.to_numeric(df["평가액(억 원)"], errors="coerce")
    df["지분율(퍼센트)"] = pd.to_numeric(df["지분율(퍼센트)"], errors="coerce")
    df = df.dropna(subset=["평가액(억 원)", "지분율(퍼센트)"])

    # --------------------------------------
    # 📊 기본 통계
    # --------------------------------------
    st.subheader("기초 통계 요약")
    col1, col2, col3 = st.columns(3)
    col1.metric("평균 평가액(억 원)", f"{df['평가액(억 원)'].mean():,.1f}")
    col2.metric("평균 지분율(%)", f"{df['지분율(퍼센트)'].mean():.2f}")
    col3.metric("상관계수", f"{df['평가액(억 원)'].corr(df['지분율(퍼센트)']):.3f}")

    # --------------------------------------
    # 📈 Altair 시각화
    # --------------------------------------
    st.subheader("평가액과 지분율의 관계 시각화")

    # 값 조정 슬라이더 (이상치 제거용)
    max_value = st.slider("최대 평가액(억 원) 필터", 
                          min_value=float(df["평가액(억 원)"].min()), 
                          max_value=float(df["평가액(억 원)"].max()), 
                          value=float(df["평가액(억 원)"].quantile(0.95)))

    filtered = df[df["평가액(억 원)"] <= max_value]

    # Altair 차트 구성
    scatter_chart = (
        alt.Chart(filtered)
        .mark_circle(size=60, opacity=0.7)
        .encode(
            x=alt.X("평가액(억 원):Q", title="평가액 (억 원)", scale=alt.Scale(zero=False)),
            y=alt.Y("지분율(퍼센트):Q", title="지분율 (%)", scale=alt.Scale(zero=False)),
            tooltip=["종목명", "평가액(억 원)", "지분율(퍼센트)"]
        )
        .interactive()
        .properties(height=500)
        .configure_axis(labelFontSize=12, titleFontSize=13)
    )

    # 회귀선 추가
    regression = (
        scatter_chart
        + scatter_chart.transform_regression("평가액(억 원)", "지분율(퍼센트)").mark_line(color="red")
    )

    st.altair_chart(regression, use_container_width=True)

    # --------------------------------------
    # 📉 분석 요약
    # --------------------------------------
    st.markdown("### 🔍 분석 요약")
    st.write(f"""
    - 데이터 개수: **{len(df):,}개 종목**
    - 평가액 상위 10개 종목 평균 지분율: **{df.nlargest(10, '평가액(억 원)')['지분율(퍼센트)'].mean():.2f}%**
    - 전체 상관관계: **{df['평가액(억 원)'].corr(df['지분율(퍼센트)']):.3f}**
    """)
    st.markdown("> 빨간 선은 단순 선형 회귀선으로, 평가액이 높을수록 지분율이 증가하는 경향을 확인할 수 있습니다.")
else:
    st.info("👆 CSV 파일을 업로드하면 자동으로 분석이 시작됩니다.")


