import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="사교육비 분석 대시보드", layout="wide")

@st.cache_data
def load_data(file_path):
    try:
        # 첫 번째 연도 행을 무시하고 두 번째 행을 헤더로 사용 
        df = pd.read_csv(file_path, header=1, encoding='utf-8')
    except UnicodeDecodeError:
        # UTF-8 실패 시 CP949로 재시도
        df = pd.read_csv(file_path, header=1, encoding='cp949')
    
    # 중복된 컬럼명 뒤에 번호를 붙여 고유하게 만듦 (2019 평균, 2020 평균 등 구분)
    return df

# 데이터 로드
grade_df = load_data('학생_성적_구간별_학생_1인당_월평균_사교육비_20251229155327.csv')
region_df = load_data('지역별_학생_1인당_월평균_사교육비_20251229155018.csv')

st.title("📊 학생 사교육비 데이터 분석 앱")

# --- 1. 성적 구간별 분석 섹션 ---
st.header("1. 성적 구간별 사교육비 및 학습 제안")

# 2024년 데이터는 파일의 가장 마지막 쪽에 위치함 [cite: 1, 2]
# 성적 구간 버튼 설정
segments = ["상위10% 이내 (만원)", "11 ~ 30% (만원)", "31 ~ 60% (만원)", "61 ~ 80% (만원)", "81 ~ 100% (만원)"]
# 2024년에 해당하는 컬럼 인덱스 추출 (데이터 구조상 마지막 5개)
actual_cols = grade_df.columns[-5:].tolist()
segment_map = dict(zip(segments, actual_cols))

# 가로 버튼 나열
cols = st.columns(len(segments))
if 'selected_seg' not in st.session_state:
    st.session_state.selected_seg = segments[0]

for i, seg in enumerate(segments):
    if cols[i].button(seg.split(" ")[0]): # 버튼 이름은 짧게 표시
        st.session_state.selected_seg = seg

current_seg_col = segment_map[st.session_state.selected_seg]

# 시각화용 데이터 필터링
subjects = ["국어", "영어", "수학", "사회, 과학"] # 
types = ["개인과외", "학원수강", "유료인터넷 및 통신강좌 등"] # 

grade_viz_data = grade_df[grade_df.iloc[:, 0].isin(subjects + types)]

fig_grade = px.bar(grade_viz_data, x=grade_df.columns[0], y=current_seg_col,
                   title=f"2024년 {st.session_state.selected_seg} 지출 현황",
                   color=grade_df.columns[0], text_auto=True)
st.plotly_chart(fig_grade, use_container_width=True)

# 제안 텍스트 로직
sub_max = grade_df[grade_df.iloc[:, 0].isin(subjects)].set_index(grade_df.columns[0])[current_seg_col].idxmax()
type_max = grade_df[grade_df.iloc[:, 0].isin(types)].set_index(grade_df.columns[0])[current_seg_col].idxmax()

st.subheader("💡 분석 기반 공부 방안 제안")
st.info(f"📍 **{st.session_state.selected_seg}** 학생 그룹 분석 결과:")
st.write(f"- **과목 측면:** 현재 **{sub_max}**에 지출이 가장 높습니다. 부족한 점을 보완하기 위해 {sub_max} 학습에 집중 투자가 필요할 수 있습니다.")
st.write(f"- **유형 측면:** 현재 **{type_max}** 방식을 가장 많이 활용 중입니다. {type_max}의 장점을 극대화하여 학습 효율을 높이시기 바랍니다.")

st.divider()

# --- 2. 지역별 분석 섹션 ---
st.header("2. 지역별 사교육비 분포")

chart_choice = st.radio("시각화 형식을 선택하세요", ["막대그래프", "원그래프", "꺾은선그래프"], horizontal=True)

# 2024년 지역 데이터 추출 (마지막 7개 열: 평균, 대도시, 서울, 광역시, 대도시이외, 중소도시, 읍면지역) [cite: 3]
regions = ["서  울 (만원)", "광역시 (만원)", "중소도시 (만원)", "읍면지역 (만원)"]
# '사교육비' 행의 데이터 추출 [cite: 3]
region_vals = region_df[region_df.iloc[:, 0] == "사교육비"].iloc[0]

region_plot_df = pd.DataFrame({
    "지역": ["서울", "광역시", "중소도시", "읍면지역"],
    "지출액": [region_vals["서  울 (만원).5"], region_vals["광역시 (만원).5"], 
               region_vals["중소도시 (만원).5"], region_vals["읍면지역 (만원).5"]] 
    # .5는 pandas가 중복 컬럼명을 피하기 위해 자동으로 붙인 2024년 데이터 접미사입니다.
})

if chart_choice == "막대그래프":
    fig_reg = px.bar(region_plot_df, x="지역", y="지출액", color="지역")
elif chart_choice == "원그래프":
    fig_reg = px.pie(region_plot_df, values="지출액", names="지역")
else:
    fig_reg = px.line(region_plot_df, x="지역", y="지출액", markers=True)

st.plotly_chart(fig_reg, use_container_width=True)
