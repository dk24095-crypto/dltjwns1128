import streamlit as st
import pandas as pd
import altair as alt

# ----------------------------------------
# 기본 설정
# ----------------------------------------
st.set_page_config(page_title="국민연금 투자 리스크 분석", layout="wide")

st.title("📊 국민연금 국내주식 투자 리스크 평가")
st.markdown("""
이 앱은 **국민연금공단의 국내 주식 투자 데이터**를 기반으로  
포트폴리오의 **집중도**와 **지분율 변동성**을 이용해  
간단한 **투자 리스크 지표**를 시각적으로 평가합니다.
""")

# ----------------------------------------
# 파일 업로드
# ----------------------------------------
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding="cp949")
    except:
        df = pd.read_csv(uploaded_file, encoding="utf-8-sig")

    st.subheader("데이터 미리보기")
    st.dataframe(df.head())

    # 숫자형 변환
    df["평가액(억 원)"] = pd.to_numeric(df["평가액(억 원)"], errors="coerce")
    df["지분율(퍼센트)"] = pd.to_numeric(df["지분율(퍼센트)"], errors="coerce")
    df = df.dropna(subset=["평가액(억 원)", "지분율(퍼센트)"])

    # ----------------------------------------
    # 리스크 계산 함수
    # ----------------------------------------
    total_value = df["평가액(억 원)"].sum()
    df["비중"] = df["평가액(억 원)"] / total_value

    # 지니계수 기반 집중도 리스크
    sorted_share = df["비중"].sort_values().values
    n = len(sorted_share)
    cumulative = sorted_share.cumsum()
    gini = 1 - (2 / (n - 1)) * (n - cumulative.sum())

    # 지분율 표준편차 기반 변동성 리스크
    volatility = df["지분율(퍼센트)"].std()

    # 종합 리스크 점수 (0~100 스케일)
    risk_score = (gini * 70) + (min(volatility, 30) * 1.0)

    # ----------------------------------------
    # 요약 통계
    # ----------------------------------------
    st.subheader("📈 리스크 지표 요약")
    col1, col2, col3 = st.columns(3)
    col1.metric("총 투자 종목 수", f"{len(df):,}개")
    col2.metric("지니계수 (집중도)", f"{gini:.3f}")
    col3.metric("리스크 점수 (0~100)", f"{risk_score:.1f}")

    # ----------------------------------------
    # 시각화 ① 상위 N개 종목 집중도
    # ----------------------------------------
    st.subheader("1️⃣ 상위 종목 집중도")

    top_n = st.slider("상위 종목 개수", 5, 30, 10)
    top_df = df.nlargest(top_n, "평가액(억 원)").copy()
    top_df["비중(%)"] = top_df["비중"] * 100

    pie_chart = (
        alt.Chart(top_df)
        .mark_arc(outerRadius=120)
        .encode(
            theta="비중(%):Q",
            color=alt.Color("종목명:N", legend=None),
            tooltip=["종목명", "비중(%)"]
        )
        .properties(height=350)
    )
    st.altair_chart(pie_chart, use_container_width=True)
    st.caption(f"상위 {top_n}개 종목이 전체의 {top_df['비중'].sum()*100:.2f}% 차지")

    # ----------------------------------------
    # 시각화 ② 지분율 분포
    # ----------------------------------------
    st.subheader("2️⃣ 지분율(%) 분포")

    hist_chart = (
        alt.Chart(df)
        .mark_bar(opacity=0.8)
        .encode(
            alt.X("지분율(퍼센트):Q", bin=alt.Bin(maxbins=40), title="지분율 (%)"),
            alt.Y("count():Q", title="종목 수"),
            tooltip=[alt.Tooltip("count():Q", title="종목 수")]
        )
        .properties(height=350)
    )
    st.altair_chart(hist_chart, use_container_width=True)

    # ----------------------------------------
    # 시각화 ③ 리스크 지표 비교 바차트
    # ----------------------------------------
    st.subheader("3️⃣ 리스크 구성 요소")

    risk_df = pd.DataFrame({
        "리스크 유형": ["집중도 (지니계수)", "변동성 (지분율 표준편차)"],
        "값": [gini * 100, volatility]
    })

    bar_chart = (
        alt.Chart(risk_df)
        .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
        .encode(
            x=alt.X("리스크 유형:N", title=None),
            y=alt.Y("값:Q", title="값 (정규화 지표)"),
            color=alt.Color("리스크 유형:N", legend=None),
            tooltip=["리스크 유형", "값"]
        )
        .properties(height=300)
    )
    st.altair_chart(bar_chart, use_container_width=True)

    # ----------------------------------------
    # 종합 해석
    # ----------------------------------------
    st.markdown("### 🔍 분석 해석")
    st.write(f"""
    - **지니계수 {gini:.3f}** → 포트폴리오 집중도가 {'높습니다' if gini > 0.5 else '낮습니다'}  
    - **지분율 변동성 {volatility:.2f}%** → 기업별 보유 비중이 {'균일하지 않습니다' if volatility > 5 else '상대적으로 균일합니다'}  
    - **종합 리스크 점수 {risk_score:.1f}/100** →  
      {('⚠️ 다소 높은 투자 집중 리스크가 존재합니다.' if risk_score > 60 else '✅ 비교적 안정적인 분산 투자 구조입니다.')}
    """)
else:
    st.info("👆 CSV 파일을 업로드하면 자동으로 리스크 분석이 시작됩니다.")
