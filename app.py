import streamlit as st
import pandas as pd
import datetime
import os
import plotly.express as px

# 데이터 파일 설정 (CSV)
DATA_FILE = "ledger_data.csv"

# 데이터 불러오기 함수
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['날짜'] = pd.to_datetime(df['날짜'])
        return df
    else:
        return pd.DataFrame(columns=["날짜", "유형", "카테고리", "금액", "메모"])

# 데이터 저장 함수
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 메인 앱 구성
st.set_page_config(page_title="나의 스마트 가계부", layout="wide")
st.title("💰 파이썬 스마트 가계부")

# 사이드바: 내역 입력
st.sidebar.header("📝 새로운 내역 입력")
with st.sidebar.form("input_form", clear_on_submit=True):
    date = st.date_input("날짜", datetime.date.today())
    type = st.selectbox("유형", ["지출", "수입"])
    category = st.selectbox("카테고리", ["식비", "교통비", "쇼핑", "주거/통신", "의료", "여가", "월급", "용돈", "기타"])
    amount = st.number_input("금액", min_value=0, step=100)
    memo = st.text_input("메모")
    submit = st.form_submit_button("기록하기")

# 데이터 로드
df = load_data()

# 데이터 추가 로직
if submit:
    new_data = {"날짜": date, "유형": type, "카테고리": category, "금액": amount, "메모": memo}
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    save_data(df)
    st.success(f"기록 완료: {category} - {amount:,}원")
    st.rerun()

# --- 통계 및 그래프 섹션 ---
if not df.empty:
    # 1. 상단 요약 지표
    total_income = df[df["유형"] == "수입"]["금액"].sum()
    total_expense = df[df["유형"] == "지출"]["금액"].sum()
    balance = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("총 수입", f"{total_income:,}원")
    col2.metric("총 지출", f"{total_expense:,}원", delta_color="inverse")
    col3.metric("현재 잔액", f"{balance:,}원")

    st.divider()

    # 2. 통계 그래프
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("📍 카테고리별 지출 현황")
        expense_df = df[df["유형"] == "지출"]
        if not expense_df.empty:
            fig_pie = px.pie(expense_df, values='금액', names='카테고리', hole=0.3)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("지출 내역이 없습니다.")

    with col_chart2:
        st.subheader("📅 월별 수입/지출 추이")
        df['월'] = df['날짜'].dt.strftime('%Y-%m')
        trend_df = df.groupby(['월', '유형'])['금액'].sum().reset_index()
        fig_bar = px.bar(trend_df, x='월', y='금액', color='유형', barmode='group')
        st.plotly_chart(fig_bar, use_container_width=True)

    # 3. 상세 내역 표
    st.subheader("📑 최근 기록 전체보기")
    st.dataframe(df.sort_values(by="날짜", ascending=False), use_container_width=True)

    # 데이터 삭제 기능
    if st.button("전체 기록 초기화"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.warning("모든 데이터가 삭제되었습니다.")
            st.rerun()
else:
    st.info("기록된 내역이 없습니다. 왼쪽 사이드바에서 첫 입력을 시작해 보세요!")