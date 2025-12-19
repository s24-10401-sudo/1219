import streamlit as st
import pandas as pd

def main():
    st.set_page_config(page_title="기온 변화 분석", layout="wide")
    
    st.title("🌡️ 지난 110년 기온 변화 분석기")
    st.write("외부 라이브러리 설치 없이 스트림릿 기본 기능만으로 구현된 분석기입니다.")

    # 1. 데이터 불러오기
    try:
        # 파일 읽기 (제공된 파일명 사용)
        df = pd.read_csv('test_copy.py.csv', encoding='cp949')
        
        # 컬럼명 앞뒤 공백 제거
        df.columns = [col.strip() for col in df.columns]
        
        # '날짜' 컬럼에서 탭(\t) 제거 및 데이트타임 변환
        df['날짜'] = df['날짜'].str.replace('\t', '').str.strip()
        df['날짜'] = pd.to_datetime(df['날짜'])
        
        # 연도 추출
        df['연도'] = df['날짜'].dt.year
        
    except Exception as e:
        st.error(f"데이터를 읽어오는 중 오류가 발생했습니다. 파일명을 확인해주세요: {e}")
        return

    # 2. 분석 기간 설정
    min_year = int(df['연도'].min())
    max_year = int(df['연도'].max())
    
    st.sidebar.header("📅 분석 설정")
    year_range = st.sidebar.slider(
        "분석할 연도를 선택하세요",
        min_year, max_year, (min_year, max_year)
    )

    # 데이터 필터링
    filtered_df = df[(df['연도'] >= year_range[0]) & (df['연도'] <= year_range[1])]

    # 3. 연도별 평균 기온 계산
    # '평균기온(℃)' 컬럼을 기준으로 연도별 평균을 구합니다.
    annual_avg = filtered_df.groupby('연도')['평균기온(℃)'].mean()

    # 4. 시각화 (Matplotlib 대신 Streamlit 내장 차트 사용)
    st.subheader(f"📈 {year_range[0]}년 ~ {year_range[1]}년 평균 기온 변화")
    
    # st.line_chart는 별도 설치 없이 바로 사용 가능합니다.
    st.line_chart(annual_avg)

    # 5. 분석 결과 요약
    st.divider()
    
    if not annual_avg.empty:
        start_temp = annual_avg.iloc[0]
        end_temp = annual_avg.iloc[-1]
        diff = end_temp - start_temp
        
        col1, col2, col3 = st.columns(3)
        col1.metric("시작 연도 기온", f"{start_temp:.2f} ℃")
        col2.metric("종료 연도 기온", f"{end_temp:.2f} ℃")
        col3.metric("기온 변화량", f"{diff:.2f} ℃", delta=f"{diff:.2f} ℃")
        
        if diff > 0:
            st.success(f"✅ 분석 결과: 지난 기간 동안 기온이 약 **{diff:.2f}도 상승**한 것을 확인할 수 있습니다.")
        else:
            st.info(f"ℹ️ 분석 결과: 지난 기간 동안 기온이 약 **{abs(diff):.2f}도 하락**했습니다.")

    # 데이터 미리보기
    with st.expander("데이터 상세 보기"):
        st.dataframe(filtered_df)

if __name__ == "__main__":
    main()
