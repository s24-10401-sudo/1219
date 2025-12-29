import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# 페이지 설정
st.set_page_config(page_title="서울시 응급실 찾기", layout="wide")

# 데이터 로드 함수 (경로 오류 방지)
@st.cache_data
def load_data():
    file_path = '서울시 응급실 위치 정보.csv'
    if not os.path.exists(file_path):
        st.error(f"파일을 찾을 수 없습니다: {file_path}. 깃허브에 파일이 업로드되었는지 확인하세요.")
        return pd.DataFrame()
    
    # encoding='utf-8' 혹은 'cp949' 확인 필요 (업로드된 파일 특성에 맞춰 utf-8 설정)
    df = pd.read_csv(file_path)
    df['병원위도'] = pd.to_numeric(df['병원위도'], errors='coerce')
    df['병원경도'] = pd.to_numeric(df['병원경도'], errors='coerce')
    return df.dropna(subset=['병원위도', '병원경도'])

df = load_data()

st.title("🚑 서울시 응급실 정보 서비스")

if not df.empty:
    # 사이드바 검색
    st.sidebar.header("🔍 검색 필터")
    search_time = st.sidebar.text_input("운영 시작 시간 (예: 0830)", "")
    search_addr = st.sidebar.text_input("주소 검색 (구/동 단위)", "")

    # 데이터 필터링
    filtered_df = df.copy()
    if search_time:
        time_cols = [col for col in df.columns if '진료시간' in col and 'S' in col]
        mask = df[time_cols].apply(lambda x: x.astype(str).str.contains(search_time)).any(axis=1)
        filtered_df = filtered_df[mask]
    
    if search_addr:
        filtered_df = filtered_df[filtered_df['주소'].str.contains(search_addr)]

    # 화면 분할
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🏥 병원 목록")
        # 검색 결과 상위 5개 표시
        display_items = filtered_df.head(5)
        if not display_items.empty:
            for _, row in display_items.iterrows():
                with st.expander(f"{row['기관명']}"):
                    st.write(f"📍 {row['주소']}")
                    st.write(f"📞 대표: {row['대표전화1']}")
                    st.write(f"🚨 응급: {row['응급실전화']}")
        else:
            st.info("검색 결과가 없습니다.")

    with col2:
        st.subheader("🗺️ 지도 위치")
        # 지도 중심점 설정
        lat, lon = (filtered_df.iloc[0]['병원위도'], filtered_df.iloc[0]['병원경도']) if not filtered_df.empty else (37.5665, 126.9780)
        
        m = folium.Map(location=[lat, lon], zoom_start=12)
        for _, row in filtered_df.head(20).iterrows():
            folium.Marker(
                [row['병원위도'], row['병원경도']],
                popup=f"<b>{row['기관명']}</b><br>{row['대표전화1']}",
                tooltip=row['기관명']
            ).add_to(m)
        
        st_folium(m, width="100%", height=500)
