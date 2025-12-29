import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# 페이지 설정
st.set_page_config(page_title="서울시 응급실 검색", layout="wide")

@st.cache_data
def load_data():
    file_path = '서울시 응급실 위치 정보.csv'
    if not os.path.exists(file_path):
        st.error(f"파일을 찾을 수 없습니다: {file_path}")
        return pd.DataFrame()

    # 인코딩 오류 방지를 위해 cp949와 utf-8 순차 시도
    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        df = pd.read_csv(file_path, encoding='utf-8')
    
    # 위도, 경도 숫자 변환
    df['병원위도'] = pd.to_numeric(df['병원위도'], errors='coerce')
    df['병원경도'] = pd.to_numeric(df['병원경도'], errors='coerce')
    return df.dropna(subset=['병원위도', '병원경도'])

df = load_data()

st.title("🚑 서울시 응급실 위치 기반 검색 서비스")

if not df.empty:
    # --- 사이드바 검색창 ---
    st.sidebar.header("🔍 검색 조건 입력")
    
    # 1. 운영 시간 검색
    search_time = st.sidebar.text_input("운영 시작 시간 (예: 0830, 0900)", help="입력하신 시간에 진료를 시작하는 병원을 찾습니다.")
    
    # 2. 주소 검색 (구/동 단위)
    search_addr = st.sidebar.text_input("주소 입력 (예: 강남구, 자양동)", "")

    # 필터링 로직
    filtered_df = df.copy()

    # 시간 필터링 (진료 시작 시간 'S' 컬럼들 중 하나라도 일치하면 표시)
    if search_time:
        start_time_cols = [col for col in df.columns if ')S' in col]
        time_mask = df[start_time_cols].apply(lambda x: x.astype(str).str.contains(search_time)).any(axis=1)
        filtered_df = filtered_df[time_mask]

    # 주소 필터링 및 결과 상위 5개 추출
    if search_addr:
        filtered_df = filtered_df[filtered_df['주소'].str.contains(search_addr, na=False)]

    # --- 결과 화면 ---
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("🏥 검색 결과 병원 리스트")
        
        # 주소 검색어가 있을 경우 가장 가까운(상위) 5개 리스트업
        if search_addr:
            st.write(f"'{search_addr}' 주변 검색 결과 중 상위 5개 병원입니다.")
            display_df = filtered_df.head(5)
        else:
            display_df = filtered_df.head(10) # 기본 10개 표시

        if not display_df.empty:
            for _, row in display_df.iterrows():
                with st.expander(f"📍 {row['기관명']}"):
                    st.write(f"**주소:** {row['주소']}")
                    st.write(f"**대표전화:** {row['대표전화1']}")
                    st.write(f"**응급실전화:** {row['응급실전화']}")
                    if st.button(f"지도로 보기 ({row['기관명'][:5]}...)", key=row['기관ID']):
                        st.session_state['center'] = [row['병원위도'], row['병원경도']]
        else:
            st.warning("일치하는 병원이 없습니다.")

    with col2:
        st.subheader("🗺️ 위치 시각화")
        
        # 지도 중심점 설정
        if 'center' in st.session_state:
            map_center = st.session_state['center']
        elif not filtered_df.empty:
            map_center = [filtered_df.iloc[0]['병원위도'], filtered_df.iloc[0]['병원경도']]
        else:
            map_center = [37.5665, 126.9780] # 서울 중심

        m = folium.Map(location=map_center, zoom_start=13)

        # 마커 추가
        for _, row in filtered_df.head(20).iterrows(): # 성능 위해 20개까지만 마커 표시
            popup_text = f"""
            <b>{row['기관명']}</b><br>
            전화: {row['대표전화1']}<br>
            응급: {row['응급실전화']}
            """
            folium.Marker(
                [row['병원위도'], row['병원경도']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=row['기관명'],
                icon=folium.Icon(color='red', icon='plus', prefix='fa')
            ).add_to(m)

        st_folium(m, width="100%", height=600)

else:
    st.error("데이터를 불러올 수 없습니다. 파일명과 위치를 확인하세요.")
