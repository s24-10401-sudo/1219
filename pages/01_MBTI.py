import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="Global MBTI Analysis", layout="wide")

# 1. 파일 로드 (경로 및 파일명 오류 방지)
@st.cache_data
def load_data():
    file_name = 'countries.csv'
    
    # 현재 폴더에 파일이 있는지 확인
    if not os.path.exists(file_name):
        return None
    
    df = pd.read_csv(file_name)
    return df

df = load_data()

if df is None:
    st.error("❌ 'countries.csv' 파일을 찾을 수 없습니다. 파일이 파이썬 코드와 같은 폴더에 업로드되었는지 확인해주세요.")
    st.info("팁: 파일 이름이 'Countries.csv'(대문자 C)인지 확인하고 코드의 파일명을 맞춰주세요.")
else:
    st.title("🌏 국가별 MBTI 성향 및 한국 비교 분석")
    
    # --- 섹션 1: 전 세계 MBTI 평균 비율 ---
    st.header("📊 전 세계 MBTI 평균 분포")
    # 수치 데이터만 추출하여 평균 계산
    numeric_df = df.drop(columns=['Country'])
    avg_series = numeric_df.mean().sort_values(ascending=False)
    
    st.bar_chart(avg_series)
    
    # --- 섹션 2: 유형별 상위 국가 & 한국 순위 ---
    st.header("🏆 MBTI 유형별 분석")
    mbti_list = numeric_df.columns.tolist()
    selected_mbti = st.selectbox("분석할 MBTI 유형을 선택하세요", mbti_list)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"{selected_mbti} 비율 상위 10개국")
        top_10 = df[['Country', selected_mbti]].sort_values(by=selected_mbti, ascending=False).head(10)
        st.dataframe(top_10, use_container_width=True)
        
    with col2:
        st.subheader("🇰🇷 한국(South Korea) 순위 및 비교")
        # 한국 데이터 검색 (South Korea 또는 Korea 포함된 행)
        korea_row = df[df['Country'].str.contains('Korea', case=False, na=False)]
        
        if not korea_row.empty:
            korea_val = korea_row[selected_mbti].values[0]
            # 전체 순위 계산
            rank = df[selected_mbti].rank(ascending=False).loc[korea_row.index[0]]
            
            st.metric(label=f"한국 내 {selected_mbti} 비율", value=f"{korea_val:.2%}")
            st.write(f"전 세계 **{int(rank)}위** / 총 {len(df)}개국")
            
            # 평균 대비 차이
            world_avg = avg_series[selected_mbti]
            diff = korea_val - world_avg
            st.write(f"세계 평균({world_avg:.2%}) 대비 **{diff:+.2%}** 차이")
        else:
            st.warning("데이터셋에서 'Korea' 관련 국가명을 찾을 수 없습니다.")

    # --- 섹션 3: 국가 간 비교 (Heatmap 스타일) ---
    st.header("🔍 국가별 상세 비교")
    target_countries = st.multiselect("비교할 국가들을 선택하세요", df['Country'].unique(), default=['South Korea'] if 'South Korea' in df['Country'].values else [df['Country'].iloc[0]])
    
    if target_countries:
        compare_df = df[df['Country'].isin(target_countries)].set_index('Country')
        st.line_chart(compare_df.T)
        st.dataframe(compare_df)
