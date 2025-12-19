import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 한글 폰트 설정 (Streamlit Cloud의 리눅스 환경을 고려하여 기본 폰트 사용)
# 차트에서 마이너스 기호가 깨지는 현상을 방지합니다.
plt.rcParams['axes.unicode_minus'] = False

def main():
    st.title("🌡️ 지난 110년 기온 변화 분석기")
    st.write("업로드된 서울 기온 데이터를 바탕으로 기온 상승 추세를 분석합니다.")

    # 1. 데이터 불러오기
    try:
        # 파일 내 날짜 데이터의 탭 문자(\t)와 공백을 처리하며 읽어옵니다.
        df = pd.read_csv('test_copy.py.csv', encoding='cp949')
        
        # 컬럼명 정리 (날짜, 평균기온 등)
        df.columns = [col.strip() for col in df.columns]
        
        # '날짜' 컬럼 전처리 (문자열 내 탭 제거 및 데이트타임 변환)
        df['날짜'] = df['날짜'].str.replace('\t', '').str.strip()
        df['날짜'] = pd.to_datetime(df['날짜'])
        
        # 연도 컬럼 생성
        df['연도'] = df['날짜'].dt.year
        
    except Exception as e:
        st.error(f"데이터를 읽어오는 중 오류가 발생했습니다: {e}")
        return

    # 2. 분석 옵션 선택
    st.sidebar.header("분석 설정")
    year_range = st.sidebar.slider(
        "분석 기간 선택",
        int(df['연도'].min()),
        int(df['연도'].max()),
        (1907, 2024)
    )

    # 데이터 필터링
    filtered_df = df[(df['연도'] >= year_range[0]) & (df['연도'] <= year_range[1])]

    # 3. 연도별 평균 기온 계산
    annual_temp = filtered_df.groupby('연도')['평균기온(℃)'].mean()

    # 4. 시각화
    st.subheader(f"📈 {year_range[0]}년 ~ {year_range[1]}년 평균 기온 추이")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(annual_temp.index, annual_temp.values, marker='o', linestyle='-', color='orangered', markersize=3)
    
    # 추세선 추가 (간단한 선형 회귀 느낌)
    import numpy as np
    z = np.polyfit(annual_temp.index, annual_temp.values, 1)
    p = np.poly1d(z)
    ax.plot(annual_temp.index, p(annual_temp.index), "b--", alpha=0.5, label="Trend Line")

    ax.set_xlabel("Year")
    ax.set_ylabel("Average Temperature (℃)")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

    # 5. 통계 요약
    st.divider()
    col1, col2 = st.columns(2)
    
    first_year_avg = annual_temp.iloc[0]
    last_year_avg = annual_temp.iloc[-1]
    diff = last_year_avg - first_year_avg

    col1.metric("시작 연도 평균", f"{first_year_avg:.2f} ℃")
    col2.metric("종료 연도 평균", f"{last_year_avg:.2f} ℃", delta=f"{diff:.2f} ℃")

    st.info(f"선택한 기간 동안 평균 기온이 약 **{diff:.2f}도** {'상승' if diff > 0 else '하락'}했습니다.")

if __name__ == "__main__":
    main()
