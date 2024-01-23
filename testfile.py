import streamlit as st
# 웹 페이지 기본 구성
st.set_page_config(
    page_icon="🖥",
    page_title="경보 관리 시스템",
    layout="wide"
)


# tabs 만들기 
tab1, tab2 = st.tabs(["경보 확인", "경보 현황"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.info('hello')
        
    with col2:
        st.info('bye')