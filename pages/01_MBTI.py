import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="Global MBTI Analysis", layout="wide")

@st.cache_data
def load_data():
    file_name = 'countries.csv'
    if not os.path.exists(file_name):
        return None
    return pd.read_csv(file_name)

df = load_data()

if df is None:
    st.error("❌ 'countries.csv' 파일을 찾을 수 없습니다.")
else:
    st.title("🌏 MBTI 유형 간 상관관계 분석")
    
    # 수치 데이터만 추출
    numeric_df = df.drop(columns=['Country'])
    
    # --- 질문: "분포가 비슷한 유형은?" ---
    st.header("🔍 분포가 비슷한 유형은? (Correlation Heatmap)")
    st.markdown("""
    이 히트맵은 국가별 비율 데이터를 바탕으로 **어떤 MBTI 유형들이 서로 유사하게 나타나는지** 보여줍니다. 
    색이 진할수록(1에 가까울수록) 두 유형은 특정 국가에서 함께 나타나는 경향이 강합니다.
    """)

    # 상관계수 계산
    corr = numeric_df.corr()

    # Matplotlib을 이용한 Heatmap 생성
    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
    
    # 축 설정
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=90, fontsize=8)
    ax.set_yticklabels(corr.columns, fontsize=8)
    
    # 컬러바 추가
    plt.colorbar(im, ax=ax)
    plt.title("MBTI Type Distribution Correlation")
    
    st.pyplot(fig)

    # --- 분석 결과 요약 ---
    st.subheader("💡 분석 가이드")
    
    # 상관관계가 높은 쌍 추출 (자기 자신 제외)
    corr_unstacked = corr.unstack()
    high_corr = corr_unstacked[corr_unstacked < 1].sort_values(ascending=False).drop_duplicates().head(5)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**가장 유사한 분포를 보이는 유형 TOP 5:**")
        for i, (types, val) in enumerate(high_corr.items()):
            st.write(f"{i+1}. {types[0]} & {types[1]}: `{val:.2f}`")
            
    with col2:
        st.info("""
        **해석 방법:**
        * **양의 상관관계(붉은색/높은 수치):** 한 유형이 많은 국가에서 다른 유형도 많이 나타납니다. (유사한 환경적/문화적 요인 공유)
        * **음의 상관관계(푸른색/낮은 수치):** 한 유형이 많으면 다른 유형은 적게 나타나는 경향이 있습니다.
        """)
