import streamlit as st

# 페이지 설정: 브라우저 탭 이름과 아이콘
st.set_page_config(page_title="Simple App", page_icon="주제 선정 진짜 개힘들어", layout="centered")

# CSS를 이용해 화면 정중앙 배치 및 디자인 커스텀
st.markdown("""
    <style>
    /* 기본 메뉴와 헤더 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 중앙 정렬 컨테이너 */
    .main-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 80vh; /* 화면 높이의 80% 사용 */
    }
    
    .centered-text {
        font-size: 100px;
        font-weight: bold;
        color: #333333;
    }
    </style>
    
    <div class="main-container">
        <div class="centered-text">주제 선정 진짜 개힘들어</div>
    </div>
    """, unsafe_allow_html=True)
