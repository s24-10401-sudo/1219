import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="기온 상승 분석기", layout="wide")

# 1. 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    # 데이터 읽기
    df = pd.read_csv('test.csv')
    
    # '날짜' 컬럼의 탭(\t) 기호 제거 및 데이트타임 변환
    df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.strip()
    df['날짜'] = pd.to_datetime(df['날짜'])
    
    # '연도' 컬럼 추출
    df['연도'] = df['날짜'].dt.year
    
    # 분석에 필요한 컬럼만 선택하고 결측치 제거
    df = df[['연도', '평균기온(℃)']].dropna()
    return df

# 앱 UI 시작
st.title("🌡️ 지난 110년 동안 정말 더워졌을까?")
st.write("업로드된 `test.csv` 데이터를 분석하여 기온 변화 추이를 확인합니다.")

try:
    df = load_data()

    # 2. 연도별 평균 기온 계산
    annual_temp = df.groupby('연도')['평균기온(℃)'].mean()

    # 3. 주요 지표 표시 (Metric)
    st.subheader("📌 주요 데이터 요약")
    col1, col2, col3 = st.columns(3)
    
    start_year = int(annual_temp.index.min())
    end_year = int(annual_temp.index.max())
    
    # 초기 10년 vs 최근 10년 평균 비교
    start_avg = annual_temp.head(10).mean()
    end_avg = annual_temp.tail(10).mean()
    diff = end_avg - start_avg

    col1.metric("분석 시작 연도", f"{start_year}년")
    col2.metric("최근 데이터 연도", f"{end_year}년")
    col3.metric("기온 변화 (약 110년)", f"{diff:.2f} ℃", delta=f"{diff:.2f} ℃")

    # 4. 그래프 시각화
    st.subheader("📈 연도별 평균 기온 변화 추이")
    # Streamlit 내장 차트 사용 (별도 라이브러리 불필요)
    st.line_chart(annual_temp)

    # 5. 심층 분석 결과 설명
    st.divider()
    st.subheader("🔍 분석 결과 요약")
    
    if diff > 0:
        st.error(f"**상승 확인:** 지난 110여 년간 평균 기온이 약 **{diff:.2f}℃ 상승**했습니다.")
        st.write(f"- 관측 초기 10년({start_year}~ ) 평균: `{start_avg:.2f}℃` 쪽")
        st.write(f"- 최근 10년(~ {end_year}) 평균: `{end_avg:.2f}℃` 쪽")
        st.info("데이터상으로 지구 온난화 혹은 도시화로 인한 기온 상승 추세가 뚜렷하게 나타납니다.")
    else:
        st.success("기온이 상승하지 않았거나 변화가 미미합니다.")

    # 6. 원본 데이터 확인
    with st.expander("데이터 표 확인하기"):
        st.dataframe(annual_temp)

except Exception as e:
    st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")
    st.info("폴더에 'test.csv' 파일이 있는지, 그리고 데이터 형식이 맞는지 확인해주세요.")
