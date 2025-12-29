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

    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        df = pd.read_csv(file_path, encoding='utf-8')
    
    # 위도, 경도 숫자 변환 및 데이터 정제
    df['병원위도'] = pd.to_numeric(df['병원위도'], errors='coerce')
    df['병원경도'] = pd.to_numeric(df['병원경도'], errors='coerce')
    return df.dropna(subset=['병원위도', '병원경도'])

def parse_to_min(t_str):
    """HH:mm 또는 HHMM 형식을 분 단위 정수로 변환"""
    try:
        clean_t = str(t_str).replace(":", "").replace(".0", "").zfill(4)
        return int(clean_t[:2]) * 60 + int(clean_t[2:])
    except:
        return None

def check_operating(row, input_time):
    """입력 시간이 병원 운영 시간 내에 있는지 확인"""
    curr_min = parse_to_min(input_time)
    if curr_min is None: return False
    
    # 모든 요일 중 하나라도 해당 시간에 운영하면 포함 (응급실 특성 반영)
    days = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    for day in days:
        s_min = parse_to_min(row.get(f'진료시간({day})S'))
        c_min = parse_to_min(row.get(f'진료시간({day})C'))
        
        if s_min is None or c_min is None: continue
        
        if c_min <= s_min: # 자정 넘어 운영하는 경우
            if curr_min >= s_min or curr_min <= c_min: return True
        else:
            if s_min <= curr_min <= c_min: return True
    return False

df = load_data()

st.title("🏥 서울시 구/동별 응급실 실시간 검색")

# 사이드바 설정
st.sidebar.header("🔍 검색 필터")
search_time = st.sidebar.text_input("검색 시간 (예: 09:30, 21:00)", placeholder="HH:MM")
search_addr = st.sidebar.text_input("검색 주소 (구 또는 동 입력)", placeholder="예: 강남구 또는 자양동")

filtered_df = df.copy()

# 1. 시간 필터링
if search_time:
    mask = filtered_df.apply(lambda r: check_operating(r, search_time), axis=1)
    filtered_df = filtered_df[mask]

# 2. 주소 필터링
if search_addr:
    filtered_df = filtered_df[filtered_df['주소'].str.contains(search_addr, na=False)]

# 화면 구성
col1, col2 = st.columns([1, 1.5])

with col1:
    if search_addr:
        st.subheader(f"📍 '{search_addr}' 지역 병원 리스트")
    else:
        st.subheader("🏥 병원 리스트 (전체)")

    if not filtered_df.empty:
        # 상위 5개 강조 리스트
        st.write(f"총 {len(filtered_df)}개의 병원이 운영 중입니다.")
        display_items = filtered_df.head(5)
        
        for _, row in display_items.iterrows():
            with st.expander(f"🏢 {row['기관명']}"):
                st.write(f"**주소:** {row['주소']}")
                st.write(f"**응급전화:** :red[{row['응급실전화']}]")
                st.write(f"**대표전화:** {row['대표전화1']}")
                st.markdown(f"[🔗 네이버 지도에서 보기](https://map.naver.com/v5/search/{row['기관명']})")
    else:
        st.warning("조건에 맞는 병원을 찾을 수 없습니다.")

with col2:
    st.subheader("🗺️ 지도 시각화")
    # 지도 중심점 계산
    lat, lon = 37.5665, 126.9780
    if not filtered_df.empty:
        lat, lon = filtered_df.iloc[0]['병원위도'], filtered_df.iloc[0]['병원경도']
    
    m = folium.Map(location=[lat, lon], zoom_start=12)
    
    for _, row in filtered_df.iterrows():
        folium.Marker(
            [row['병원위도'], row['병원경도']],
            popup=folium.Popup(f"<b>{row['기관명']}</b><br>{row['응급실전화']}", max_width=250),
            tooltip=row['기관명'],
            icon=folium.Icon(color='red', icon='plus', prefix='fa')
        ).add_to(m)
    
    st_folium(m, width="100%", height=600)
