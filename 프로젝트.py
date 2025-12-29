import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="사교육비 분석 대시보드", layout="wide")

# 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    # 1. 성적 구간별 데이터 로드 (첫 두 줄이 헤더 성격)
    grade_df = pd.read_csv('학생_성적_구간별_학생_1인당_월평균_사교육비_20251229155327.csv', encoding='utf-8')
    # 2. 지역별 데이터 로드
    region_df = pd.read_csv('지역별_학생_1인당_월평균_사교육비_20251229155018.csv', encoding='utf-8')
    
    # 열 이름 재설정 (연도와 구간 결합)
    # 실제 데이터 구조에 맞춰 2024년 데이터를 타겟으로 설정 (가장 최신)
    # 예시 데이터 구조에 근거하여 컬럼 인덱스를 수동 지정하거나 매핑 필요
    return grade_df, region_df

grade_data, region_data = load_data()

# 분석에 사용할 성적 구간 리스트
segments = ["상위10% 이내", "11 ~ 30%", "31 ~ 60%", "61 ~ 80%", "81 ~ 100%"]
# 2024년 컬럼 매핑 (데이터 파일 구조 기반 - 실제 인덱스 확인 필요)
# 데이터 스니펫 기준으로 마지막 6개 컬럼이 2024년 데이터임
col_2024 = {
    "평균": grade_data.columns[-6],
    "상위10% 이내": grade_data.columns[-5],
    "11 ~ 30%": grade_data.columns[-4],
    "31 ~ 60%": grade_data.columns[-3],
    "61 ~ 80%": grade_data.columns[-2],
    "81 ~ 100%": grade_data.columns[-1]
}

st.title("📊 학생 사교육비 지출 데이터 분석")
st.markdown("---")

# --- SECTION 1: 성적 구간별 분석 ---
st.header("1. 성적 구간별 사교육비 및 공부 제안")

# 가로 버튼 나열
st.write("분석할 성적 구간을 선택하세요:")
cols = st.columns(len(segments))
selected_segment = st.session_state.get('selected_segment', segments[0])

for i, seg in enumerate(segments):
    if cols[i].button(seg):
        selected_segment = seg
        st.session_state['selected_segment'] = seg

st.subheader(f"📍 선택된 구간: {selected_segment}")

# 데이터 필터링 (과목군 vs 유형군 분리)
# 실제 데이터의 '과목 및 유형' 열 내용에 따라 필터링
subjects = ["국어", "영어", "수학", "사회·과학", "논술"]
types = ["개인과외", "그룹과외", "학원강습", "학습지", "인터넷·통신"]

target_col = col_2024[selected_segment]

# 시각화 데이터 준비
plot_df = grade_data[grade_data.iloc[:, 0].isin(subjects + types)]
fig_grade = px.bar(plot_df, x=grade_data.columns[0], y=target_col, 
                   title=f"{selected_segment} 성적대 항목별 지출액",
                   labels={target_col: "지출액 (만원)", grade_data.columns[0]: "항목"},
                   color=target_col, color_continuous_scale="Viridis")
st.plotly_chart(fig_grade, use_container_width=True)

# 최고 지출 항목 추출 및 공부 방안 제안
subject_max = grade_data[grade_data.iloc[:, 0].isin(subjects)].set_index(grade_data.columns[0])[target_col].idxmax()
type_max = grade_data[grade_data.iloc[:, 0].isin(types)].set_index(grade_data.columns[0])[target_col].idxmax()

st.info(f"💡 **{selected_segment} 구간 분석 결과 및 제안**")
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"**✅ 과목 분석:** 현재 **{subject_max}**에 가장 많은 비용을 쓰고 있습니다. **{subject_max}** 학습 시 사교육의 도움을 적극 활용하는 것을 권장합니다.")
with c2:
    st.markdown(f"**✅ 유형 분석:** 현재 **{type_max}** 형태의 지출이 가장 높습니다. 학습 효율을 높이기 위해 **{type_max}** 방식을 지속하거나 강화해보세요.")

st.markdown("---")

# --- SECTION 2: 지역별 데이터 분석 ---
st.header("2. 지역별 사교육비 분포")

# 시각화 선택 라디오 버튼
chart_type = st.radio("시각화 형식을 선택하세요:", ["막대그래프", "원그래프", "꺾은선그래프"], horizontal=True)

# 2024년 지역 데이터 추출 (마지막 7개 컬럼 기준: 평균, 서울, 광역시, 중소도시, 읍면지역 등)
# 데이터 구조에 맞춰 지역 컬럼 리스트 정의
region_cols = ["서  울 (만원)", "광역시 (만원)", "중소도시 (만원)", "읍면지역 (만원)"]
# 2024년도 행(보통 첫 번째 또는 전체 평균 행 제외 필요) 필터링
# 여기서는 '전체 평균(국어/영어/수학 합계)'에 해당하는 행을 예시로 사용
latest_region_data = region_data[region_data.iloc[:, 0] == "전체"].iloc[0] # 실제 데이터에 '전체' 행이 있다고 가정

# 차트 데이터 생성
chart_data = pd.DataFrame({
    "지역": ["서울", "광역시", "중소도시", "읍면지역"],
    "지출액": [region_data.iloc[0, -5], region_data.iloc[0, -4], region_data.iloc[0, -2], region_data.iloc[0, -1]] # 예시 인덱스
})

if chart_type == "막대그래프":
    fig_region = px.bar(chart_data, x="지역", y="지출액", color="지역", title="지역별 사교육비 지출 현황")
elif chart_type == "원그래프":
    fig_region = px.pie(chart_data, values="지출액", names="지역", title="지역별 사교육비 비중")
else:
    fig_region = px.line(chart_data, x="지역", y="지출액", markers=True, title="지역별 사교육비 추이(비교)")

st.plotly_chart(fig_region, use_container_width=True)

st.success("데이터 분석이 완료되었습니다. 위 차트와 제안을 확인해주세요!")
