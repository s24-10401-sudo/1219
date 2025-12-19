import streamlit as st
import pandas as pd
import os

def main():
    st.set_page_config(page_title="기온 변화 분석", layout="wide")
    st.title("🌡️ 지난 110년 기온 변화 분석기")

    # 1. 파일 자동 찾기 기능 추가
    target_file = 'test_copy.py.csv'
    
    # 만약 지정된 파일이 없다면 현재 폴더에서 csv 파일을 검색
    if not os.path.exists(target_file):
        all_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if all_files:
            target_file = all_files[0] # 첫 번째 csv 파일을 선택
        else:
            st.error("❌ 폴더 내에서 CSV 파일을 찾을 수 없습니다. 파일이 업로드되었는지 확인해주세요.")
            st.info(f"현재 폴더 파일 목록: {os.listdir('.')}")
            return

    # 2. 데이터 불러오기
    try:
        # 파일 인코딩은 한국 공공데이터 표준인 cp949 혹은 utf-8-sig를 시도합니다.
        df = pd.read_csv(target_file, encoding='cp949')
        
        # 컬럼명 전처리
        df.columns = [col.strip().replace('"', '') for col in df.columns]
        
        # '날짜' 데이터 정제 (따옴표, 탭 제거)
        df['날짜'] = df['날짜'].astype(str).str.replace(r'[\t"\s]', '', regex=True)
        df['날짜'] = pd.to_datetime(df['날짜'])
        df['연도'] = df['날짜'].dt.year
        
    except Exception as e:
        st.error(f"데이터 분석 중 오류 발생: {e}")
        return

    # 3. 사이드바 기간 설정
    st.sidebar.header("📅 분석 설정")
    min_y, max_y = int(df['연도'].min()), int(df['연도'].max())
    year_range = st.sidebar.slider("분석 기간", min_y, max_y, (min_y, max_y))

    # 데이터 필터링 및 연도별 평균 계산
    filtered_df = df[(df['연도'] >= year_range[0]) & (df['연도'] <= year_range[1])]
    annual_avg = filtered_df.groupby('연도')['평균기온(℃)'].mean()

    # 4. 시각화 (내장 차트 사용 - 별도 설치 불필요)
    st.subheader(f"📈 {year_range[0]}년 ~ {year_range[1]}년 기온 변화 추이")
    st.line_chart(annual_avg)

    # 5. 결과 요약
    if not annual_avg.empty:
        start_v = annual_avg.iloc[0]
        end_v = annual_avg.iloc[-1]
        diff = end_v - start_v
        
        c1, c2, c3 = st.columns(3)
        c1.metric("시작 연도 평균", f"{start_v:.2f} ℃")
        c2.metric("종료 연도 평균", f"{end_v:.2f} ℃")
        c3.metric("총 변화량", f"{diff:.2f} ℃", delta=f"{diff:.2f} ℃")

        st.divider()
        if diff > 0:
            st.success(f"🌞 지난 {len(annual_avg)}년간 기온이 약 **{diff:.2f}도 상승**했음을 확인할 수 있습니다.")
        else:
            st.info(f"❄️ 해당 기간 동안 기온이 약 **{abs(diff):.2f}도 하락**했습니다.")

if __name__ == "__main__":
    main()
