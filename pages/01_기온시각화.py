import streamlit as st
import pandas as pd

def main():
    st.set_page_config(page_title="기온 변화 분석", layout="wide")
    st.title("🌡️ 지난 110년 기온 변화 분석기")
    st.write("업로드된 데이터를 바탕으로 기온 상승 추세를 확인합니다.")

    # 1. 데이터 불러오기
    file_name = 'test.py.csv'
    try:
        # 데이터의 한글 깨짐 방지를 위해 cp949 인코딩 사용
        df = pd.read_csv(file_name, encoding='cp949')
        
        # 컬럼명 및 날짜 데이터 정제
        df.columns = [col.strip() for col in df.columns]
        df['날짜'] = df['날짜'].astype(str).str.replace('\t', '').str.strip()
        df['날짜'] = pd.to_datetime(df['날짜'])
        df['연도'] = df['날짜'].dt.year
        
    except FileNotFoundError:
        st.error(f"파일을 찾을 수 없습니다. '{file_name}' 파일이 같은 폴더에 있는지 확인해주세요.")
        return
    except Exception as e:
        st.error(f"데이터 분석 중 오류가 발생했습니다: {e}")
        return

    # 2. 분석 설정 (사이드바)
    st.sidebar.header("📅 분석 설정")
    min_year = int(df['연도'].min())
    max_year = int(df['연도'].max())
    
    year_range = st.sidebar.slider(
        "분석 기간 선택",
        min_year, max_year, (min_year, max_year)
    )

    # 3. 데이터 필터링 및 계산
    filtered_df = df[(df['연도'] >= year_range[0]) & (df['연도'] <= year_range[1])]
    
    # 연도별 평균 기온 계산
    annual_avg = filtered_df.groupby('연도')['평균기온(℃)'].mean()

    # 4. 시각화 (스트림릿 내장 차트 사용 - 별도 라이브러리 불필요)
    st.subheader(f"📈 {year_range[0]}년 ~ {year_range[1]}년 평균 기온 추이")
    st.line_chart(annual_avg)

    # 5. 결과 해석 및 요약
    st.divider()
    if not annual_avg.empty:
        start_val = annual_avg.iloc[0]
        end_val = annual_avg.iloc[-1]
        diff = end_val - start_val

        col1, col2, col3 = st.columns(3)
        col1.metric("시작 연도 평균", f"{start_val:.2f} ℃")
        col2.metric("종료 연도 평균", f"{end_val:.2f} ℃")
        col3.metric("기온 변화량", f"{diff:.2f} ℃", delta=f"{diff:.2f} ℃")

        st.info(f"선택한 {len(annual_avg)}년 동안 평균 기온이 약 **{abs(diff):.2f}도 {'상승' if diff > 0 else '하락'}**했습니다.")
        
        if diff > 1.0:
            st.warning("⚠️ 뚜렷한 기온 상승 추세가 관찰됩니다. 이는 지구 온난화의 영향일 가능성이 높습니다.")

    # 데이터 테이블 보기
    with st.expander("데이터 전체 보기"):
        st.write(filtered_df)

if __name__ == "__main__":
    main()
