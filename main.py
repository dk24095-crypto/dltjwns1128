import streamlit as st
import pandas as pd
import altair as alt

# --------------------------------------
# 기본 설정
# --------------------------------------
st.set_page_config(page_title="국민연금 투자 분석", layout="wide")

st.title("💹 국민연금 국내주식 투자 분석")
st.markdown("""
이 앱은 **국민연금공단의 국내주식 투자 데이터**를 바탕으로  
`평가액(억 원)`과 `지분율(퍼센트)`의 관계를 시각적으로 분석합니다.
""")

# --------------------------------------
# 파일 업로드
# --------------------------------------
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # 인코딩 자동 처리
    try:
        df = pd.read_csv(uploaded_file, encoding="cp949")
    except:
        df = pd.read_csv(uploaded_file, encoding="utf-8-sig")

    # 데이터 확인
    st.subheader("데이터 미리보기")
    st.dataframe(df.head())

    # 숫자형 컬럼 변환
    df["평가액(억 원)"] = pd.to_numeric(df["평가액(억 원)"], errors="coerce")
    df["지분율(퍼센트)"] = pd.to_numeric(df["지분율(퍼센트)"], errors="coerce")
    df = df.dropna(subset=["평가액(억 원)", "지분율(퍼센트)"])

    # --------------------------------------
    # 기본 통계
    # --------------------------------------
    st.subheader("기초 통계 요약")
    col1, col2, col3 = st.columns(3)
    col1.metric("평균 평가액(억 원)", f"{df['평가액(억 원)'].mean():,.1f}")
    col2.metric("평균 지분율(%)", f"{df['지분율(퍼센트)'].mean():.2f}")
    col3.metric("상관계수", f"{df['평가액(억 원)'].corr(df['지분율(퍼센트)']):.3f}")

    # --------------------------------------
    # Altair 시각화
    # --------------------------------------
    st.subheader("평가액과 지분율의 관계 시각화")

    max_value = st.slider(
        "최대 평가액(억 원) 필터",
        min_value=float(df["평가액(억 원)"].min()),
        max_value=float(df["평가액(억 원)"].max()),
        value=float(df["평가액(억 원)"].quantile(0.95))
    )

    filtered = df[df["평가액(억 원)"] <= max_value]

    # 산점도
    scatter = (
        alt.Chart(filtered)
        .mark_circle(size=60, opacity=0.7)
        .encode(
            x=alt.X("평가액(억 원):Q", title="평가액 (억 원)", scale=alt.Scale(zero=False)),
            y=alt.Y("지분율(퍼센트):Q", title="지분율 (%)", scale=alt.Scale(zero=False)),
            tooltip=["종목명", "평가액(억 원)", "지분율(퍼센트)"]
        )
    )

    # 회귀선
    regression_line = (
        alt.Chart(filtered)
        .transform_regression("평가액(억 원)", "지분율(퍼센트)")
        .mark_line(color="red", strokeWidth=2)
    )

    # 두 그래프를 layer로 결합
    chart = alt.layer(scatter, regression_line).interactive()

    st.altair_chart(chart, use_container_width=True)

    # --------------------------------------
    # 분석 요약
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
