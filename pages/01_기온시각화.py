import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 한글 폰트 설정 (Streamlit Cloud의 리눅스 환경에서도 그래프가 깨지지 않게 설정)
plt.rcParams['axes.unicode_minus'] = False

def main():
    st.set_page_config(page_title="기온 상승 분석기", layout="wide")
    st.title("🌡️ 지난 110년 기온 변화 분석기")
    st.write("업로드된 `test.csv` 데이터를 바탕으로 기온 상승 추세를 분석합니다.")

    # 1. 데이터 불러오기
    try:
        # 데이터에 한글이 포함되어 있으므로 cp949 인코딩 사용
        df = pd.read_csv('test.csv', encoding='cp949')
        
        # 컬럼명 앞뒤 공백 제거
        df.columns = [col.strip() for col in df.columns]
        
        # '날짜' 컬럼 정제 (탭 문자 \t 및 따옴표 제거)
        df['날짜'] = df['날짜'].astype(str).str.replace(r'[\t"\s]', '', regex=True)
        df['날짜'] = pd.to_datetime(df['날짜'])
        
        # 연도 컬럼 생성
        df['연도'] = df['날짜'].dt.year
        
    except FileNotFoundError:
        st.error("❌ 'test.csv' 파일을 찾을 수 없습니다. 파일이 같은 폴더에 있는지 확인해주세요.")
        return
    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
        return

    # 2. 사이드바 설정
    st.sidebar.header("📊 분석 설정")
    min_year, max_year = int(df['연도'].min()), int(df['연도'].max())
    year_range = st.sidebar.slider("분석 기간 선택", min_year, max_year, (min_year, max_year))

    # 데이터 필터링
    filtered_df = df[(df['연도'] >= year_range[0]) & (df['연도'] <= year_range[1])]
    
    # 연도별 평균 기온 계산
    annual_avg = filtered_df.groupby('연도')['평균기온(℃)'].mean()

    # 3. 시각화 및 분석 결과
    st.subheader(f"📈 {year_range[0]}년 ~ {year_range[1]}년 기온 추이")
    
    if not annual_avg.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # 실제 데이터 그래프
        ax.plot(annual_avg.index, annual_avg.values, label='Annual Average', color='orange', marker='o', markersize=3)
        
        # 기온 상승 추세선(Trend Line) 계산
        z = np.polyfit(annual_avg.index, annual_avg.values, 1)
        p = np.poly1d(z)
        ax.plot(annual_avg.index, p(annual_avg.index), "r--", label='Trend Line', linewidth=2)
        
        ax.set_xlabel("Year")
        ax.set_ylabel("Average Temperature (℃)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)

        # 4. 수치 요약
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        start_temp = annual_avg.iloc[0]
        end_temp = annual_avg.iloc[-1]
        temp_diff = end_temp - start_temp

        col1.metric("시작 연도 평균", f"{start_temp:.2f} ℃")
        col2.metric("종료 연도 평균", f"{end_temp:.2f} ℃")
        col3.metric("기온 변화량", f"{temp_diff:.2f} ℃", delta=f"{temp_diff:.2f} ℃")

        # 기온 상승 여부 판정
        if temp_diff > 0:
            st.success(f"✅ 분석 결과: 지난 기간 동안 기온이 약 **{temp_diff:.2f}도 상승**한 것을 확인할 수 있습니다.")
        else:
            st.info(f"ℹ️ 분석 결과: 해당 기간 동안 기온 변화가 미미하거나 소폭 하락했습니다.")
    else:
        st.warning("선택한 범위에 표시할 데이터가 없습니다.")

if __name__ == "__main__":
    main()
