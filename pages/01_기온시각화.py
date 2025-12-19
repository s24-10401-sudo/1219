import streamlit as st
import pandas as pd

def main():
    st.set_page_config(page_title="기온 변화 분석", layout="wide")
    st.title("🌡️ 기온 상승 데이터 분석기 (1907-2025)")
    st.write("지난 110여 년간의 데이터를 분석하여 기온 상승 추세를 확인합니다.")

    # 1. 데이터 불러오기
    # 스트림릿 클라우드 환경에서는 'test.csv'가 같은 경로에 있어야 합니다.
    try:
        df = pd.read_csv('test.csv', encoding='cp949')
        
        # 데이터 전처리: 컬럼명 공백 제거 및 날짜 정제
        df.columns = [col.strip() for col in df.columns]
        
        # '날짜' 컬럼의 탭(\t) 문자와 따옴표 제거 후 데이트타임 변환
        df['날짜'] = df['날짜'].astype(str).str.replace(r'[\t"\s]', '', regex=True)
        df['날짜'] = pd.to_datetime(df['날짜'])
        df['연도'] = df['날짜'].dt.year
        
    except FileNotFoundError:
        st.error("❌ 'test.csv' 파일을 찾을 수 없습니다. 파일 이름을 확인해 주세요.")
        return
    except Exception as e:
        st.error(f"❌ 데이터 로드 중 오류 발생: {e}")
        return

    # 2. 사이드바 설정
    st.sidebar.header("📅 분석 설정")
    min_year = int(df['연도'].min())
    max_year = int(df['연도'].max())
    year_range = st.sidebar.slider("분석 기간 선택", min_year, max_year, (min_year, max_year))

    # 3. 데이터 필터링 및 연도별 평균 계산
    filtered_df = df[(df['연도'] >= year_range[0]) & (df['연도'] <= year_range[1])]
    # 연도별 평균 기온 계산
    annual_avg = filtered_df.groupby('연도')['평균기온(℃)'].mean()

    # 4. 시각화 (별도 설치가 필요한 matplotlib 대신 스트림릿 내장 차트 사용)
    st.subheader(f"📈 {year_range[0]}년 ~ {year_range[1]}년 평균 기온 추이")
    st.line_chart(annual_avg)

    # 5. 상승 추세 확인 기능
    st.divider()
    if len(annual_avg) > 1:
        start_temp = annual_avg.iloc[0]
        end_temp = annual_avg.iloc[-1]
        diff = end_temp - start_temp
        
        col1, col2, col3 = st.columns(3)
        col1.metric("시작 연도 평균", f"{start_temp:.2f} ℃")
        col2.metric("종료 연도 평균", f"{end_val := annual_avg.iloc[-1]:.2f} ℃")
        col3.metric("기온 변화량", f"{diff:.2f} ℃", delta=f"{diff:.2f} ℃")

        st.info(f"선택한 기간 동안 평균 기온이 약 **{abs(diff):.2f}도 {'상승' if diff > 0 else '하락'}**했습니다.")
        
        # 110년 전체 범위를 봤을 때의 통찰 제공
        if year_range[0] <= 1910 and year_range[1] >= 2020:
            st.success("✅ **분석 결과:** 1900년대 초반에 비해 최근 기온이 뚜렷하게 상승한 것을 확인할 수 있습니다. 이는 지구 온난화의 실질적인 증거로 볼 수 있습니다.")

    # 데이터 미리보기
    with st.expander("데이터 상세 보기"):
        st.dataframe(filtered_df)

if __name__ == "__main__":
    main()
