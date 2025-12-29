import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
from datetime import time

# 페이지 설정
st.set_page_config(page_title="서울시 응급실 검색", layout="wide")

@st.cache_data
def load_data():
    file_path = '서울시 응급실 위치 정보.csv'
    if not os.path.exists(file_path):
        st.error(f"파일을 찾을 수 없습니다: {file_path}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        df = pd.read_csv(file_path, encoding='utf-8')
    
    df['병원위도'] = pd.to_numeric(df['병원위도'], errors='coerce')
    df['병원경도'] = pd.to_numeric(df['병원경도'], errors='coerce')
    return df.dropna(subset=['병원위도', '병원경도'])

def parse_time_to_minutes(t_str):
    """문자열 시간을 분(minute) 단위 정수로 변환 (예: '0930' -> 570)"""
    try:
        t_str = str(t_str).replace(".0", "").replace(":", "").zfill(4)
        hours = int(t_str[:2])
        minutes = int(t_str[2:])
        return hours * 60 + minutes
    except:
        return None

def is_open_strict(row, input_time_str):
    """입력된 시간(HH:mm)에 병원이 운영 중인지 분 단위로 비교"""
    current_total_minutes = parse_time_to_minutes(input_time_str)
    if current_total_minutes is None:
        return False
        
    days = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    for day in days:
        s_val = row.get(f'진료시간({day})S')
        c_val = row.get(f'진료시간({day})C')
        
        if pd.isna(s_val) or pd.isna(c_val):
            continue
            
        start_min = parse_time_to_minutes(s_val)
        end_min = parse_time_to_minutes(c_val)
        
        if start_min is None or end_min is None:
            continue

        # 야간 진료 (종료 시간이 다음날인 경우, 예: 09:00 ~ 02:00)
        if end_min <= start_min:
            if current_total_minutes >= start_min or current_total_minutes <= end_min:
                return True
        # 일반 진료
        else:
            if start_min <= current_total_minutes <= end_min:
                return True
    return False

df = load_data()

st.title("🚑 분 단위 실시간 응급실 검색")

if not df.empty:
    st.sidebar.header("🔍 상세 검색")
    
    # 분 단위 입력창
    search_time = st.sidebar.text_input("검색 시간 (예: 09:30, 23:10)", placeholder="HH:MM 형식")
    search_addr = st.sidebar.text_input("주소 입력 (예: 강남구, 자양동)", "")

    filtered_df = df.copy()

    # 1. 시간 필터링
    if search_time:
        with st.spinner('해당 시간에 운영 중인 병원을 선별하고 있습니다...'):
            mask = filtered_df.apply(lambda row: is_open_strict(row, search_time), axis=1)
            filtered_df = filtered_df[mask]

    # 2. 주소 필터링
    if search_addr:
        filtered_df = filtered_df[filtered_df['주소'].str.contains(search_addr, na=False)]

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("🏥 조건 부합 병원")
        # 요청하신 대로 주소 검색 시 리스트 상단 5개 강조
        count = 5 if search_addr else 10
        display_df = filtered_df.head(count)
        
        if not display_df.empty:
            st.write(f"총 {len(filtered_df)}개의 병원이 검색되었습니다.")
            for _, row in display_df.iterrows():
                with st.expander(f"➕ {row['기관명']}"):
                    st.write(f"**📍 주소:** {row['주소']}")
                    st.write(f"**📞 응급실:** {row['응급실전화']}")
                    st.write(f"**🕒 오늘 진료:** {row.get('진료시간(월요일)S', '정보없음')} ~ {row.get('진료시간(월요일)C', '정보없음')}")
        else:
            st.info("검색 조건에 맞는 병원이 없습니다.")

    with col2:
        st.subheader("🗺️ 지도 위치 확인")
        # 지도 중심 설정
        center = [37.5665, 126.9780]
        if not filtered_df.empty:
            center = [filtered_df.iloc[0]['病院위도'], filtered_df.iloc[0]['病院경도']] if '病院위도' in filtered_df else [filtered_df.iloc[0]['병원위도'], filtered_df.iloc[0]['병원경도']]
        
        m = folium.Map(location=center, zoom_start=12)
        for _, row in filtered_df.head(30).iterrows():
            folium.Marker(
                [row['병원위도'], row['병원경도']],
                popup=f"<b>{row['기관명']}</b>",
                tooltip=row['기관명'],
                icon=folium.Icon(color='red', icon='hospital', prefix='fa')
            ).add_to(m)
        st_folium(m, width="100%", height=600)
