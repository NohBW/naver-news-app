
# streamlit run naver_news_02.py

import streamlit as dt
import pandas as pd
import datetime
import requests
from bs4 import BeautifulSoup
import urllib3

# 브라우저 탭 및 모바일 환경 최적화 설정
dt.set_page_config(
    page_title="네이버 뉴스 헤드라인",
    page_icon="📰",
    layout="centered",  # 모바일 화면 가독성을 위해 중앙 집중형 레이아웃 채택
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS를 통한 모바일 UI 디자인 고도화 (하늘색 테두리 효과 및 버튼 스타일)
# [수정] unsafe_allowed_html -> unsafe_allow_html 오타 교정
dt.markdown("""
    <style>
    /* 전체 폰트 및 배경 정의 */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Malgun Gothic', -apple-system, sans-serif;
    }
    /* 타이틀바 및 시계 래퍼 스타일 */
    .custom-title-bar {
        background-color: #212121;
        color: white;
        padding: 12px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    .custom-time-label {
        font-size: 16px;
        font-weight: bold;
        text-align: center;
        color: #37474f;
        margin-bottom: 20px;
    }
    /* 뉴스 카드 스타일 및 팝업 대용 테두리 구현 */
    .news-card {
        border: 2px solid #e3f2fd;
        border-left: 5px solid #00b0ff; /* 요구사항: 하늘색 시각 피드백 포인트 */
        background-color: #ffffff;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 10px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    .news-title {
        font-size: 16px;
        font-weight: bold;
        color: #212121;
        text-decoration: none;
    }
    .news-press {
        font-size: 13px;
        color: #757575;
        margin-top: 4px;
    }
    /* 요약본 및 본문 박스 스타일링 */
    .summary-box {
        background-color: #fafafa;
        border: 1px solid #b0bec5;
        padding: 12px;
        border-radius: 6px;
        font-size: 15px;
        line-height: 1.5;
        margin-bottom: 15px;
    }
    .content-box {
        background-color: #ffffff;
        border: 1px solid #b0bec5;
        padding: 12px;
        border-radius: 6px;
        font-size: 15px;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    </style>
""", unsafe_allow_html=True)

# 네이버 뉴스 섹션 정의
SECTIONS = {
            "정치": "https://news.naver.com/section/100",
            "경제": "https://news.naver.com/section/101",
            "사회": "https://news.naver.com/section/102",
            "생활/문화": "https://news.naver.com/section/103",
            "세계": "https://news.naver.com/section/104",
            "IT/과학": "https://news.naver.com/section/105"
}

# 뉴스 본문 크롤링 및 주요 내용 3항목 요약 함수
def fetch_news_detail(url):
    if not url or url == "#":
        return "본문 주소가 유효하지 않습니다.", "URL 정보가 없어 요약할 수 없습니다."
        
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        res = requests.get(url, headers=headers, timeout=5, verify=False)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            article_body = soup.select_one("#newsct_article")
            if not article_body:
                article_body = soup.select_one("#articeBody, #newsEndContents")
                
            if article_body:
                for expr in article_body.select(".byline, .reporter_area, script, style, .vod_area"):
                    expr.extract()
                
                raw_text = article_body.get_text("\n", strip=True)
                
                # 가독성을 높인 문단 정리
                paragraphs = [p.strip() for p in raw_text.split('\n') if p.strip()]
                full_content = "\n\n".join(paragraphs)
                
                # 문장 단위 분할 후 3항목 요약 생성 로직
                sentences = [s.strip() for s in raw_text.split('.') if len(s.strip()) >= 15]
                if len(sentences) >= 3:
                    summary_text = ""
                    for i in range(3):
                        summary_text += f"**{i+1}.** {sentences[i]}.\n\n"
                else:
                    summary_text = "본문이 너무 짧아 3항목 요약을 생성할 수 없습니다."
                    
                return full_content, summary_text
            else:
                return "본문 내용을 파싱할 수 없는 페이지 유형이거나 보안이 걸려있습니다.", "요약본을 생성할 수 없습니다."
    except Exception as e:
        return f"데이터를 가져오는 중 오류가 발생했습니다: {e}", "오류 발생"
    return "내용을 불러오지 못했습니다.", "요약 실패"

# 상단 커스텀 타이틀바 및 실시간 날짜 출력
# [수정] unsafe_allowed_html -> unsafe_allow_html 오타 교정
dt.markdown('<div class="custom-title-bar">📰 네이버 뉴스 분야별 헤드라인</div>', unsafe_allow_html=True)

now = datetime.datetime.now()
weeks = ['월', '화', '수', '목', '금', '토', '일']
week_str = weeks[now.weekday()]
time_str = now.strftime(f"%Y년 %m월 %d일({week_str}요일) %H:%M:%S")
# [수정] unsafe_allowed_html -> unsafe_allow_html 오타 교정
dt.markdown(f'<div class="custom-time-label">⏱️ {time_str}</div>', unsafe_allow_html=True)

# 모바일 화면 상단에 세련되게 배치되는 카테고리 탭
selected_section = dt.tabs(list(SECTIONS.keys()))

# 세션 상태 변수 초기화 (뉴스 데이터 보존용)
if "news_store" not in dt.session_state:
    dt.session_state.news_store = {sec: [] for sec in SECTIONS}

# 데이터 수집 함수 통합 개발
def refresh_all_data():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    with dt.spinner("네이버 뉴스 실시간 헤드라인 20개를 수집하는 중..."):
        for sec, url in SECTIONS.items():
            temp_list = []
            try:
                res = requests.get(url, headers=headers, timeout=5, verify=False)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    items = soup.select(".sa_text")
                    count = 0
                    for item in items:
                        if count >= 20:
                            break
                        title_el = item.select_one(".sa_text_title, .sa_text_strong")
                        press_el = item.select_one(".sa_text_press")
                        link_el = item.select_one("a")
                        news_url = link_el["href"] if link_el and link_el.has_attr("href") else "#"
                        
                        if title_el:
                            title = title_el.get_text(strip=True)
                            press = press_el.get_text(strip=True) if press_el else "미상"
                            temp_list.append({"title": title, "press": press, "url": news_url})
                            count += 1
                dt.session_state.news_store[sec] = temp_list
            except Exception as e:
                print(f"Error: {e}")

# 하단부 기능 제어 버튼 구역
col_update, col_save = dt.columns(2)
with col_update:
    if dt.button("🔄 실시간 업데이트", use_container_width=True, type="primary"):
        refresh_all_data()

with col_save:
    all_rows = []
    for sec, items in dt.session_state.news_store.items():
        for idx, item in enumerate(items, 1):
            all_rows.append([sec, idx, item['title'], item['press'], item['url']])
    df = pd.DataFrame(all_rows, columns=["분야", "순위", "제목", "언론사", "링크 주소"])
    csv_data = df.to_csv(index=False, encoding='utf-8-sig')
    
    dt.download_button(
        label="📥 CSV 파일 저장",
        data=csv_data,
        file_name=f"naver_news_{now.strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# 최초 실행 시 데이터가 비어있으면 자동 로드 처리
if not any(dt.session_state.news_store.values()):
    refresh_all_data()

# 선택된 각 카테고리별 뉴스 리스트 렌더링
for i, sec_name in enumerate(SECTIONS.keys()):
    with selected_section[i]:
        dt.markdown(f"#### 📌 {sec_name} 헤드라인 뉴스 20")
        news_list = dt.session_state.news_store.get(sec_name, [])
        
        if not news_list:
            dt.warning("가져온 뉴스 데이터가 없습니다. 업데이트 버튼을 클릭하세요.")
        
        for idx, item in enumerate(news_list, 1):
            # 깔끔한 모바일 카드 형태 레이아웃 정의
            card_html = f"""
            <div class="news-card">
                <div class="news-title">{idx}. {item['title']}</div>
                <div class="news-press">📰 {item['press']}</div>
            </div>
            """
            # [수정] unsafe_allowed_html -> unsafe_allow_html 오타 교정
            dt.markdown(card_html, unsafe_allow_html=True)
            
            # 모바일 팝업을 직관적으로 대체하는 Streamlit Expander 컴포넌트
            with dt.expander("🔍 요약 및 본문 전체 보기"):
                with dt.spinner("해당 기사 본문을 분석하는 중..."):
                    content, summary = fetch_news_detail(item['url'])
                
                dt.markdown("### 📌 주요 내용 3항목 요약")
                # [수정] unsafe_allowed_html -> unsafe_allow_html 오타 교정
                dt.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                
                dt.markdown("### 📰 뉴스 본문 전체 내용")
                # [수정] unsafe_allowed_html -> unsafe_allow_html 오타 교정
                dt.markdown(f'<div class="content-box">{content}</div>', unsafe_allow_html=True)
