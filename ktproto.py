# 라이브러리
import pandas as pd
import streamlit as st
import numpy as np
import folium
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import date
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
from io import BytesIO, StringIO
import base64
import matplotlib.font_manager as fm

# 시각화 한글폰트 설정
# plt.rcParams['font.family'] = 'Apple SD Gothic Neo'
# # 시각화 한글폰트 설정
# plt.rc('font', family='Malgun Gothic')
# sns.set(font="Malgun Gothic",#"NanumGothicCoding", 
# rc={"axes.unicode_minus":False}, # 마이너스 부호 깨짐 현상 해결
# style='darkgrid')

# 지도 가상데이터
map_data = {
        'City': ['Busan', 'Daegu', 'Seoul', 'Gangwon', 'Chungcheong', 'Jeju', 'Jeolla'],
        'Population': [12299, 14666, 16155, 11940, 17977, 1619, 28888],
        'Latitude': [35.1796, 35.8714, 37.5665, 37.5556, 36.6347, 33.4996, 35.5658],
        'Longitude': [129.0756, 128.6014, 126.9780, 128.7250, 127.5039, 126.5312, 126.8902]
    }

df2 = pd.DataFrame(map_data)

 # 대한민국 지도
def print_map(df2):

    # 대한민국 중심 좌표
    center = [36.5, 127.5]

    # Folium 지도 생성
    map = folium.Map(location=center, zoom_start=7)

    # 각 지역에 대한 원형 마커 추가
    for i, row in df2.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=row['Population']/ 550 ,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.6,
            popup=f"{row['City']} {row['Population']:,}건"
        ).add_to(map)

    # Folium 지도를 HTML로 변환
    map.save('map.html')
    
    return folium_static(map)
    
# "Level" 강조하는 스타일 함수
def highlight_level(s):
    styles = []
    for v in s:
        if v == 7:
            styles.append('background-color: red')
        elif v == 5:
            styles.append('background-color: orange')
        elif v == 4:
            styles.append('background-color: yellow')
        else:
            styles.append('')
    return styles

df = pd.read_csv('고장이력데이터_final.csv')
all_all = pd.read_csv('전국장애현황수.csv')
all_eq = pd.read_csv('eqlist.csv')
all_warn = pd.read_csv('warncount.csv')



# -------------------- ▲ 필요 변수 생성 코딩 End ▲ --------------------


# -------------------- ▼ Streamlit 웹 화면 구성 START ▼ --------------------
# 웹 페이지 기본 구성
st.set_page_config(
    page_icon="🖥",
    page_title="경보 관리 시스템",
    layout="wide"
)

st.markdown(
    """
    <style>
@font-face {
font-family: 'GmarketSansMedium';
src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff') format('woff');
font-weight: normal;
font-style: normal;
}

html, body, [class*="css"]  {
font-family: 'GmarketSansMedium';
font-size: 12;
}
</style>

""",
    unsafe_allow_html=True,
)

# tabs 만들기 
tab1, tab2 = st.tabs(["경보 확인", "경보 현황"])

### ------------------------------ tab1 내용 구성하기 ---------------------------------------------
with tab1:
    # 사업장정보 넣기
    st.image('ktlogo.png')
    st.markdown('### 🚨 실시간 경보 관리')
    today = date.today()
    styled_df = df.style.apply(highlight_level, subset=['등급'], axis=0)
    st.info(today)
    st.dataframe(styled_df)
        
    col1, col2 = st.columns(2)
    with col1:
        
        
        st.info('핵심 항목 추출')
        selected_row_index = st.selectbox('처리할 행을 선택하세요', df.index)
    

        # 선택한 행의 'Action Details' 열 값 가져오기
        selected_system_name = df.loc[selected_row_index, '시스템명']
        selected_originate = df.loc[selected_row_index, '발생개소']
        selected_warning = df.loc[selected_row_index, '경보항목']
        selected_uni = df.loc[selected_row_index, '유니트']
        selected_originate_region = df.loc[selected_row_index, '발생국소']
        selected_region = df.loc[selected_row_index, '지역']


        # 선택한 행의 'Action Details' 열 값 표시
        st.info(f" + 장비 : {selected_system_name} \n + 발생개소 : {selected_originate} \n + 경보항목 : {selected_warning} \n + 유니트 : {selected_uni} \n + 발생국소 : {selected_originate_region} \n + 담당센터 : {selected_region} \n + 예상원인 : 미사용회선 가능성 높음(고장기간 3개월 초과)" )

        st.markdown("T-SDN 바로가기 : www.kt.tsdn.com")
        st.markdown("유니트 재고확인 : www.kt.unit.com")
        st.markdown("NeoSS-Del 바로가기 : www.kt.neossdel.com")
        st.markdown("NeoSS-FM 바로가기 : www.kt.neossfm.com")
    
    
    with col2:
        st.info('장애 위험 경보')
        
        risk_warn = ['CML_ALM', 'PTM', 'LOF', 'EBER', 'RDI']
        filtered_df = df[df['경보항목'].str.contains('|'.join(risk_warn))]
        st.dataframe(filtered_df)
        
        st.info('경보 검색')
        input_data = st.text_input('경보명을 입력하세요.')
        
        if input_data:
            # CSV 파일에서 데이터 로드
            warn_info = pd.read_csv('warnexplain.csv')

            # 검색어가 포함된 행만 선택
            filtered_data = warn_info[warn_info['경보항목'].str.contains(input_data, case=False)]

            if not filtered_data.empty:
                # 검색 결과 표시
                st.write(filtered_data)
            else:
                st.warning("검색된 결과가 없습니다.")
      
       
    # 선택한 행의 'Action Details' 열에 추가할 값을 입력 받기
    unique_input_key = f'조치내역_{selected_row_index}'
    unique_input_key_cause = f'상세원인_{selected_row_index}'
    # 클릭한 행이 있는 경우에만 처리
    if selected_row_index is not None:
        # 'Action Details' 열에 추가할 값을 입력 받기
        new_value = st.text_input('조치내역을 입력하세요.', key=unique_input_key, placeholder="키워드 중심으로 작성하세요.")
        new_value_cause = st.text_input('상세내역을 입력하세요', key=unique_input_key_cause, placeholder="특이상황 발생 시 작성하세요.")
        # 값을 입력했을 경우 'Action Details' 열에 값을 추가
        if new_value:
            # 클릭한 행에 'Action Details' 열에 새로운 값을 추가
            df.loc[selected_row_index, '조치내역'] = new_value
            df.loc[selected_row_index, '상세내역'] = new_value_cause
            st.success(f'선택한 행에 내역을 추가했습니다.')

            # 수정된 데이터 표시
            st.dataframe(df)

            # 수정된 데이터 저장
            save_path = '고장이력데이터(test.csv'
            df.to_csv(save_path, index=False)
            st.success(f'수정된 데이터를 "{save_path}"에 저장했습니다.')
            
            new_value_action = ""  # 'Action details' 입력 값 초기화
            new_value_cause = ""

### ------------------------------ tab2 내용 구성하기 ---------------------------------------------
with tab2:
    
    # 사업장정보 넣기
    st.image('ktlogo.png')
    st.markdown('### 📊 경보 현황')
    today = date.today()
    show_map = st.button('전국 경보현황')
    
  
    
    if show_map:
         print_map(df2)
    else:
        st.empty()
    
        
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        def show_plot1(selected_region):
            # 폰트 로드
            font_path = 'GmarketSansMedium.otf'  # 폰트 파일의 경로로 변경
            font_prop = fm.FontProperties(fname=font_path)
            plt.rcParams['font.family'] = font_prop.get_name()
        
            fig = plt.figure(figsize=(8,8))
            # 선택한 지역을 빨간색으로 표시
            color_palette = ['red' if region == selected_region else 'gray' for region in all_all['지역']]
            sns.barplot(data = all_all, y='지역', x='count', palette=color_palette)
            plt.title('지역별 경보 발생 현황')
            plt.show()

            st.pyplot(fig)
        # Streamlit 앱
        selected_region = st.selectbox('지역별', all_all['지역'])
        show_plot1(selected_region)
        
    with c2:

        def show_plot2(selected_eq):
            # 폰트 로드
            font_path = 'GmarketSansMedium.otf'  # 폰트 파일의 경로로 변경
            font_prop = fm.FontProperties(fname=font_path)
            plt.rcParams['font.family'] = font_prop.get_name()
            # st.selectbox('지역', all_all['지역'])
            fig = plt.figure(figsize=(5,4.17))
            # fig, ax = plt.subplots(figsize=(10, 6))
            
            # 선택된 장비의 인덱스 가져오기
            selected_eq_index = all_eq.index[all_eq['장비명'] == selected_eq].tolist()[0]

            # 선택된 장비를 제외한 나머지는 파이 차트에 회색으로 표시
            colors = ['grey' if i != selected_eq_index else 'red' for i in range(len(all_eq))]
            

            # 선택한 지역을 빨간색으로 표시
            plt.pie(all_eq['발생횟수'], labels=all_eq['장비명'], autopct='%1.1f%%', startangle=90, colors=colors)
            
            plt.title('장비별 경보 비율')
            plt.show()
           # BytesIO를 사용하여 그림을 바이트로 변환
            img_bytes = BytesIO()
            plt.savefig(img_bytes, format='png')
            img_bytes.seek(0)

            # base64로 인코딩
            img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')

            # HTML 태그를 사용하여 크기 조절 및 이미지 삽입
            st.markdown(f'<img src="data:image/png;base64,{img_base64}" alt="pie chart" style="width:100%;">', unsafe_allow_html=True)

        # Streamlit 앱
        selected_eq = st.selectbox('장비별', all_eq['장비명'])
        show_plot2(selected_eq)
        
    with c3:
        def show_plot3(selected_warn):
            # 폰트 로드
            font_path = 'GmarketSansMedium.otf'  # 폰트 파일의 경로로 변경
            font_prop = fm.FontProperties(fname=font_path)
            plt.rcParams['font.family'] = font_prop.get_name()
            fig = plt.figure(figsize=(8,8))
            # 선택한 지역을 빨간색으로 표시
            color_palette1 = ['red' if region == selected_warn else 'gray' for region in all_warn['경보항목']]
            sns.barplot(data = all_warn, y='발생횟수(합)', x='경보항목', palette=color_palette1)
            # plt.xticks(rotation=45)
            plt.title('경보횟수 Top5')
            plt.show()

            st.pyplot(fig)
        # Streamlit 앱
        selected_warn= st.selectbox('경보항목별', all_warn['경보항목'])
        show_plot3(selected_warn)
        
