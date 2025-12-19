import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 한글 폰트 설정 (Streamlit Cloud 리눅스 환경 대응)
plt.rcParams['axes.unicode_minus'] = False

def main():
    st.set_page_config(page_title="기온 변화 분석기", layout="wide")
    st.title("🌡️ 지난 110년 기온 상승 분석")
    st.write("1907년부터 현재까지의 데이터를 바탕으로 기온 변화 추이를 분석합니다.")

    # 1. 데이터 로드 (test.csv 파일 가정)
    try:
        # 파일 인코딩은 공공데이터 표준인 cp949를 우선 시도합니다.
        df = pd.read_csv('test.csv', encoding='cp949')
        
        # 컬럼명 앞뒤 공백 제거
        df.columns = [col.strip() for col in df.columns]
        
        # 날짜 데이터 정제 (따옴표, 탭 문자 제거 및 변환)
        df['날짜'] = df['날짜'].astype(str).str.replace(r'[\t"\s]', '', regex=True)
        df['날짜'] = pd.to_datetime(df['날짜'])
        df['연도'] = df['날짜'].dt.year
        
    except FileNotFoundError:
        st.error("❌ 'test.csv' 파일을 찾을 수 없습니다. 파일이 같은 폴더에 있는지 확인해주세요.")
        return
    except Exception as e:
        st.error(f"❌ 데이터 로딩 중 오류 발생: {e}")
        return

    # 2. 사이드바 기간 설정
    st.sidebar.header("📅 분석 설정")
    min_year, max_year = int(df['연도'].min()), int(df['연도'].max())
    year_range = st.sidebar.slider("분석 기간", min_year, max_year, (min_year, max_year))

    # 데이터 필터링 및 연도별 평균 계산
    filtered_df = df[(df['연도'] >= year_range[0]) & (df['연도'] <= year_range[1])]
    annual_avg = filtered_df.groupby('연도')['평균기온(℃)'].mean()

    # 3. 시각화
    st.subheader(f"📈 {year_range[0]}년 ~ {year_range[1]}년 평균 기온 추이")
    
    if not annual_avg.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(annual_avg.index, annual_avg.values, color='#ff4b4b', linewidth=2, label='Annual Avg')
        
        # 추세선 추가 (기온 상승 여부 확인용)
        import numpy as np
        z = np.polyfit(annual_avg.index, annual_avg.values, 1)
        p = np.poly1d(z)
        ax.plot(annual_avg.index, p(annual_avg.index), "b--", alpha=0.7, label='Trend Line')
        
        ax.set_xlabel("Year")
        ax.set_ylabel("Temp (℃)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

        # 4. 결과 요약 (지표 표시)
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        start_v = annual_avg.iloc[0]
        end_v = annual_avg.iloc[-1]
        diff = end_v - start_v

        col1.metric("시작 연도 평균", f"{start_v:.2f} ℃")
        col2.metric("종료 연도 평균", f"{end_v:.2f} ℃")
        col3.metric("총 변화량", f"{diff:.2f} ℃", delta=f"{diff:.2f} ℃")

        # 5. 상승 확인 메시지
        if diff > 0:
            st.success(f"✅ 분석 결과: 선택한 기간 동안 기온이 약 **{diff:.2f}도 상승**했습니다.")
        else:
            st.info(f"ℹ️ 분석 결과: 해당 기간 동안 기온이 약 **{abs(diff):.2f}도 하락**했습니다.")
            
    else:
        st.warning("선택한 범위에 데이터가 없습니다.")

if __name__ == "__main__":
    main()
