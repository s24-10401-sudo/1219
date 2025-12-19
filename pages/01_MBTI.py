import streamlit as st
import pandas as pd

# 1. 데이터 로드
@st.cache_data
def load_data():
    # 같은 폴더의 countries.csv 읽기
    df = pd.read_csv('countries.csv')
    return df

try:
    df = load_data()
    
    st.title("🌏 글로벌 MBTI 성향 분석 대시보드")
    st.markdown("전 세계 국가별 MBTI 분포 데이터를 분석하고 한국과 비교해봅니다.")

    # --- 섹션 1: 전체 국가 MBTI 평균 비율 ---
    st.header("📊 전 세계 MBTI 평균 분포")
    # 국가 컬럼을 제외한 수치 데이터의 평균 계산
    avg_mbti = df.drop(columns=['Country']).mean().sort_values(ascending=False)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.bar_chart(avg_mbti)
    with col2:
        st.write("**평균 비율 TOP 5**")
        st.dataframe(avg_mbti.head(5))

    # --- 섹션 2: MBTI 유형별 높은 국가 TOP 10 & 한국 비교 ---
    st.header("🏆 유형별 상위 국가 & 한국 순위")
    
    mbti_types = df.columns[1:].tolist()  # Country 제외한 MBTI 유형들
    selected_type = st.selectbox("분석할 MBTI 유형을 선택하세요:", mbti_types)

    # 선택한 유형의 TOP 10 추출
    top_10 = df[['Country', selected_type]].sort_values(by=selected_type, ascending=False).head(10)
    
    # 한국(South Korea) 데이터 찾기
    korea_data = df[df['Country'].str.contains('Korea|South Korea', case=False, na=False)]
    
    col3, col4 = st.columns(2)
    with col3:
        st.subheader(f"{selected_type} 비율 TOP 10")
        st.table(top_10)
        
    with col4:
        st.subheader("🇰🇷 한국 데이터")
        if not korea_data.empty:
            korea_val = korea_data[selected_type].values[0]
            # 전체 순위 계산
            rank = df[selected_type].rank(ascending=False).loc[korea_data.index[0]]
            
            st.metric(label=f"한국의 {selected_type} 비율", value=f"{korea_val:.2%}")
            st.write(f"전체 {len(df)}개국 중 **{int(rank)}위**입니다.")
        else:
            st.warning("데이터셋에서 'Korea' 정보를 찾을 수 없습니다.")

    # --- 섹션 3: 국가별 상세 분석 ---
    st.header("🔍 국가별 상세 프로필")
    selected_country = st.selectbox("국가를 선택하세요:", df['Country'].unique())
    
    country_profile = df[df['Country'] == selected_country].drop(columns=['Country']).T
    country_profile.columns = ['비율']
    
    st.line_chart(country_profile)
    st.dataframe(country_profile.sort_values(by='비율', ascending=False))

except FileNotFoundError:
    st.error("파일을 찾을 수 없습니다. 'countries.csv' 파일이 같은 폴더에 있는지 확인해주세요.")
