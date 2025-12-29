import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

# 페이지 설정
st.set_page_config(page_title="서울시 응급실 찾기", layout="wide")

# 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv('서울시 응급실 위치 정보.csv')
    # 위도, 경도 데이터 숫자형 변환
    df['병원위도'] = pd.to_numeric(df['병원위도'], errors='coerce')
    df['병원경도'] = pd.to_numeric(df['병원경도'], errors='coerce')
    return df.dropna(subset=['병원위도', '병원경도'])

df = load_data()

st.title("🚑 서울시 응급실 위치 정보 시스템")
st.markdown("특정 운영 시간대 병원 검색 및 내 위치 기반 가장 가까운 병원을 찾아보세요.")

# --- 사이드바: 검색 기능 ---
st.sidebar.header("🔍 검색 및 필터")

# 1. 운영 시간 검색 (예: 0900)
search_time = st.sidebar.text_input("운영 시작 시간 검색 (예: 0830, 0900)", "")

# 2. 주소 검색 (구/동 단위)
search_addr = st.sidebar.text_input("주소 검색 (예: 강남구, 자양동)", "")

# 데이터 필터링
filtered_df = df.copy()

if search_time:
    # 모든 요일의 시작 시간 중 해당 시간을 포함하는지 확인 (간단한 매칭)
    time_cols = [col for col in df.columns if '진료시간' in col and 'S' in col]
    mask = df[time_cols].apply(lambda x: x.str.contains(search_time)).any(axis=1)
    filtered_df = filtered_df[mask]

if search_addr:
    filtered_df = filtered_df[filtered_df['주소'].str.contains(search_addr)]

# --- 메인 화면: 결과 리스트 및 지도 ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🏥 병원 리스트")
    if not filtered_df.empty:
        # 가장 가까운 5개 로직 (주소 검색 시)
        display_df = filtered_df.head(5) if search_addr else filtered_df.head(10)
        for i, row in display_df.iterrows():
            with st.expander(f"**{row['기관명']}**"):
                st.write(f"📍 주소: {row['주소']}")
                st.write(f"📞 전화: {row['대표전화1']}")
                st.write(f"🚑 응급전화: {row['응급실전화']}")
    else:
        st.warning("검색 결과가 없습니다.")

with col2:
    st.subheader("🗺️ 응급실 위치 지도")
    
    # 지도 중심 설정 (데이터가 있으면 첫 번째 데이터 위치, 없으면 서울 중심)
    if not filtered_df.empty:
        center_lat = filtered_df.iloc[0]['병원위도']
        center_lon = filtered_df.iloc[0]['병원경도']
    else:
        center_lat, center_lon = 37.5665, 126.9780
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # 마커 추가
    for i, row in filtered_df.head(20).iterrows(): # 성능을 위해 상위 20개만 표시
        popup_html = f"""
            <div style="width:200px">
                <h4>{row['기관명']}</h4>
                <p><b>주소:</b> {row['주소']}</p>
                <p><b>전화:</b> {row['대표전화1']}</p>
                <a href="https://map.kakao.com/link/to/{row['기관명']},{row['병원위도']},{row['병원경도']}" target="_blank">길찾기 바로가기</a>
            </div>
        """
        folium.Marker(
            [row['병원위도'], row['병원경도']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['기관명'],
            icon=folium.Icon(color='red', icon='plus', prefix='fa')
        ).add_to(m)

    st_folium(m, width=800, height=500)
