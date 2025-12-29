import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# 페이지 설정
st.set_page_config(page_title="서울시 응급실 정보", layout="wide")

@st.cache_data
def load_data():
    # 파일명에 괄호나 공백이 있으면 에러가 날 수 있으므로 파일명을 가급적 단순하게 바꾸는 것이 좋습니다.
    file_path = '서울시 응급실 위치 정보.csv' 
    
    if not os.path.exists(file_path):
        st.error(f"파일을 찾을 수 없습니다: {file_path}")
        return pd.DataFrame()

    try:
        # 1. 먼저 utf-8로 시도
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            # 2. 실패하면 cp949(한글 윈도우 표준)로 시도
            df = pd.read_csv(file_path, encoding='cp949')
        except Exception as e:
            st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
            return pd.DataFrame()
            
    # 위도 경도 변환 및 결측치 제거
    df['병원위도'] = pd.to_numeric(df['병원위도'], errors='coerce')
    df['병원경도'] = pd.to_numeric(df['병원경도'], errors='coerce')
    return df.dropna(subset=['병원위도', '병원경도'])

df = load_data()

# --- 이후 UI 코드는 이전과 동일하게 작성 ---
st.title("🚑 서울시 응급실 위치 정보 시스템")

if not df.empty:
    # 검색창 (구/동 단위)
    search_addr = st.text_input("📍 계신 곳의 주소를 입력하세요 (예: 강남구, 자양동)", "")
    
    filtered_df = df.copy()
    if search_addr:
        filtered_df = df[df['주소'].str.contains(search_addr, na=False)]
        # 주소 검색 시 상위 5개만 리스트로 보여줌
        st.subheader(f"🔍 '{search_addr}' 주변 응급실 (가까운 순 5개)")
        results = filtered_df.head(5)
        
        for _, row in results.iterrows():
            st.info(f"🏥 **{row['기관명']}**\n\n📍 주소: {row['주소']}\n\n📞 응급실: {row['응급실전화']}")

    # 지도 시각화
    st.subheader("🗺️ 전체 지도 확인")
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)
    for _, row in filtered_df.iterrows():
        folium.Marker(
            [row['병원위도'], row['병원경도']],
            popup=f"<b>{row['기관명']}</b><br>{row['응급실전화']}",
            tooltip=row['기관명']
        ).add_to(m)
    st_folium(m, width="100%", height=500)
