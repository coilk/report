import streamlit as st
import openai
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="에이텍 보고서 초안 생성기",
    page_icon="📄",
    layout="wide",
)

# ────────────────────────── CSS ──────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

.report-header {
    background: linear-gradient(135deg, #1a3a5c 0%, #2e6da4 100%);
    color: white;
    padding: 24px 32px;
    border-radius: 12px 12px 0 0;
    margin-bottom: 0;
}
.report-header h1 {
    margin: 0;
    font-size: 1.6rem;
    letter-spacing: 2px;
}
.report-header p {
    margin: 4px 0 0;
    opacity: 0.75;
    font-size: 0.85rem;
}

.report-body {
    border: 1.5px solid #2e6da4;
    border-top: none;
    border-radius: 0 0 12px 12px;
    padding: 28px 32px;
    background: #ffffff;
    margin-bottom: 24px;
}

.section-title {
    font-size: 0.78rem;
    font-weight: 700;
    color: #1a3a5c;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    border-left: 3px solid #2e6da4;
    padding-left: 8px;
    margin-bottom: 10px;
    margin-top: 18px;
}

.approval-grid {
    display: grid;
    gap: 8px;
}
.approval-cell {
    border: 1.5px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px 14px;
    background: #f8fafc;
    min-height: 72px;
}
.approval-cell .label {
    font-size: 0.7rem;
    color: #64748b;
    font-weight: 600;
    margin-bottom: 4px;
}
.approval-cell .name {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1e293b;
}
.approval-cell.empty {
    opacity: 0.45;
    border-style: dashed;
}

.draft-box {
    background: #f0f7ff;
    border: 1.5px solid #93c5fd;
    border-radius: 10px;
    padding: 22px 26px;
    white-space: pre-wrap;
    font-size: 0.92rem;
    line-height: 1.85;
    color: #1e293b;
}

.file-badge {
    display: inline-block;
    background: #e0f2fe;
    border: 1px solid #7dd3fc;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    color: #0369a1;
    margin: 3px;
}

.divider {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 18px 0;
}

.stButton>button {
    border-radius: 8px;
    font-family: 'Noto Sans KR', sans-serif;
    font-weight: 600;
}
</style>
""",
    unsafe_allow_html=True,
)

# ────────────────────────── Session state init ──────────────────────────
if "approval_line" not in st.session_state:
    st.session_state.approval_line = [""] * 4
if "consensus_line" not in st.session_state:
    st.session_state.consensus_line = [""] * 4
if "attachments" not in st.session_state:
    st.session_state.attachments = []
if "ref_docs" not in st.session_state:
    st.session_state.ref_docs = []
if "draft" not in st.session_state:
    st.session_state.draft = ""

# ────────────────────────── Header ──────────────────────────
st.markdown(
    """
<div class="report-header">
    <h1>📄 에이텍 보고서 초안 생성기</h1>
    <p>AI 기반 업무 보고서 초안 자동 작성 시스템</p>
</div>
<div class="report-body">
""",
    unsafe_allow_html=True,
)

# ────────────────────────── 기본 정보 ──────────────────────────
st.markdown('<div class="section-title">기본 정보</div>', unsafe_allow_html=True)

col_date, col_dept, col_writer = st.columns([1, 1, 1])
with col_date:
    report_date = st.date_input("작성일", value=date.today(), label_visibility="visible")
with col_dept:
    department = st.text_input("부서명", placeholder="예) 기술연구소 개발1팀")
with col_writer:
    writer = st.text_input("작성자", placeholder="홍길동")

report_title = st.text_input(
    "보고서 제목",
    placeholder="예) 2026년 2분기 AI 솔루션 개발 현황 보고",
    help="보고서의 제목을 입력하세요.",
)

col_type, col_priority = st.columns([1, 1])
with col_type:
    report_type = st.selectbox(
        "보고서 유형",
        ["업무 현황 보고", "기술 검토 보고", "사업 제안 보고", "예산 집행 보고", "프로젝트 진행 보고", "기타"],
    )
with col_priority:
    priority = st.selectbox("중요도", ["일반", "중요", "긴급"])

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ────────────────────────── 보고서 목적/내용 ──────────────────────────
st.markdown('<div class="section-title">보고 목적 및 주요 내용</div>', unsafe_allow_html=True)

report_purpose = st.text_area(
    "보고 목적",
    placeholder="이 보고서를 작성하는 목적을 간략히 입력하세요.",
    height=80,
)

report_content = st.text_area(
    "주요 내용 / 키워드",
    placeholder="보고서에 포함할 주요 내용, 키워드, 수치, 배경 등을 자유롭게 입력하세요.\n예) AI 솔루션 3건 개발 완료, 특허 출원 2건, 3분기 출시 예정, 예산 집행율 78%",
    height=130,
)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ────────────────────────── 결재 라인 ──────────────────────────
st.markdown('<div class="section-title">결재 / 합의 라인</div>', unsafe_allow_html=True)

tab_approval, tab_consensus = st.tabs(["✅ 결재 라인", "🤝 합의 라인"])

with tab_approval:
    st.caption("결재권자를 순서대로 입력하세요 (최대 4칸). 비워두면 해당 칸은 표시되지 않습니다.")
    ap_cols = st.columns(4)
    for i, col in enumerate(ap_cols):
        with col:
            st.session_state.approval_line[i] = st.text_input(
                f"결재 {i+1}",
                value=st.session_state.approval_line[i],
                placeholder=f"결재자 {i+1}",
                key=f"ap_{i}",
            )

with tab_consensus:
    st.caption("합의 대상자를 순서대로 입력하세요 (최대 4칸). 비워두면 해당 칸은 표시되지 않습니다.")
    cn_cols = st.columns(4)
    for i, col in enumerate(cn_cols):
        with col:
            st.session_state.consensus_line[i] = st.text_input(
                f"합의 {i+1}",
                value=st.session_state.consensus_line[i],
                placeholder=f"합의자 {i+1}",
                key=f"cn_{i}",
            )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ────────────────────────── 첨부 파일 ──────────────────────────
st.markdown('<div class="section-title">첨부 파일</div>', unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "첨부 파일 선택 (복수 선택 가능)",
    accept_multiple_files=True,
    type=["pdf", "docx", "xlsx", "pptx", "png", "jpg", "jpeg", "txt", "hwp"],
    key="file_uploader",
    label_visibility="collapsed",
)

if uploaded_files:
    for uf in uploaded_files:
        if uf.name not in [a["name"] for a in st.session_state.attachments]:
            st.session_state.attachments.append({"name": uf.name, "size": uf.size})

if st.session_state.attachments:
    st.markdown("**첨부된 파일:**")
    cols_remove = st.columns([6, 1])
    to_remove = []
    for idx, att in enumerate(st.session_state.attachments):
        c1, c2 = st.columns([6, 1])
        with c1:
            kb = att["size"] / 1024
            st.markdown(
                f'<span class="file-badge">📎 {att["name"]} ({kb:.1f} KB)</span>',
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("삭제", key=f"del_att_{idx}", use_container_width=True):
                to_remove.append(idx)
    for idx in sorted(to_remove, reverse=True):
        st.session_state.attachments.pop(idx)
    if to_remove:
        st.rerun()

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ────────────────────────── 참조 결재 문서 ──────────────────────────
st.markdown('<div class="section-title">참조 결재 문서 첨부</div>', unsafe_allow_html=True)
st.caption("참조할 이전 결재 문서나 관련 공문을 첨부하세요.")

ref_files = st.file_uploader(
    "참조 결재 문서 선택",
    accept_multiple_files=True,
    type=["pdf", "docx", "xlsx", "pptx", "txt", "hwp"],
    key="ref_uploader",
    label_visibility="collapsed",
)

if ref_files:
    for rf in ref_files:
        if rf.name not in [r["name"] for r in st.session_state.ref_docs]:
            st.session_state.ref_docs.append({"name": rf.name, "size": rf.size})

if st.session_state.ref_docs:
    st.markdown("**참조 문서:**")
    to_remove_ref = []
    for idx, rd in enumerate(st.session_state.ref_docs):
        c1, c2 = st.columns([6, 1])
        with c1:
            kb = rd["size"] / 1024
            st.markdown(
                f'<span class="file-badge">📋 {rd["name"]} ({kb:.1f} KB)</span>',
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("삭제", key=f"del_ref_{idx}", use_container_width=True):
                to_remove_ref.append(idx)
    for idx in sorted(to_remove_ref, reverse=True):
        st.session_state.ref_docs.pop(idx)
    if to_remove_ref:
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ────────────────────────── 초안 생성 버튼 ──────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

generate_col, clear_col = st.columns([3, 1])
with generate_col:
    generate_btn = st.button(
        "✨ AI 보고서 초안 생성",
        type="primary",
        use_container_width=True,
    )
with clear_col:
    if st.button("초기화", use_container_width=True):
        st.session_state.draft = ""
        st.session_state.attachments = []
        st.session_state.ref_docs = []
        st.session_state.approval_line = [""] * 4
        st.session_state.consensus_line = [""] * 4
        st.rerun()

# ────────────────────────── GPT 초안 생성 ──────────────────────────
def build_prompt(title, purpose, content, report_type, priority, department, writer, date_str, approval, consensus, attachments, ref_docs):
    ap_list = [a for a in approval if a.strip()]
    cn_list = [c for c in consensus if c.strip()]
    att_list = [a["name"] for a in attachments]
    ref_list = [r["name"] for r in ref_docs]

    prompt = f"""당신은 대한민국 IT 기업 '에이텍(ATEC)'의 전문 보고서 작성 어시스턴트입니다.
아래 정보를 바탕으로 사내 결재용 보고서 초안을 작성하세요.

---
[보고서 정보]
- 작성일: {date_str}
- 부서: {department or '미입력'}
- 작성자: {writer or '미입력'}
- 제목: {title or '(제목 없음)'}
- 유형: {report_type}
- 중요도: {priority}
- 보고 목적: {purpose or '미입력'}
- 주요 내용/키워드: {content or '미입력'}
- 결재 라인: {', '.join(ap_list) if ap_list else '없음'}
- 합의 라인: {', '.join(cn_list) if cn_list else '없음'}
- 첨부 파일: {', '.join(att_list) if att_list else '없음'}
- 참조 결재 문서: {', '.join(ref_list) if ref_list else '없음'}
---

작성 지침:
1. 에이텍 사내 결재 문서 형식에 맞게, 공식적이고 간결한 문체로 작성하세요.
2. 구성: ① 보고 목적 ② 배경 및 현황 ③ 주요 내용 ④ 향후 계획 및 기대효과 ⑤ 건의/요청 사항 (필요 시)
3. 각 항목은 번호와 소제목을 명확히 표기하세요.
4. 중요도가 '긴급'인 경우 서두에 긴급 표시를 추가하세요.
5. 첨부 파일이 있으면 문서 말미에 '붙임' 항목으로 나열하세요.
6. 참조 결재 문서가 있으면 '참조' 항목으로 나열하세요.
7. 보고서는 A4 1~2페이지 분량으로 작성하세요.

지금 바로 보고서 본문만 작성하세요. 추가 설명 없이 보고서 내용만 출력하세요.
"""
    return prompt


if generate_btn:
    if not report_title.strip() and not report_content.strip():
        st.warning("보고서 제목 또는 주요 내용을 입력해주세요.")
    else:
        with st.spinner("AI가 보고서 초안을 작성 중입니다..."):
            try:
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                prompt = build_prompt(
                    title=report_title,
                    purpose=report_purpose,
                    content=report_content,
                    report_type=report_type,
                    priority=priority,
                    department=department,
                    writer=writer,
                    date_str=str(report_date),
                    approval=st.session_state.approval_line,
                    consensus=st.session_state.consensus_line,
                    attachments=st.session_state.attachments,
                    ref_docs=st.session_state.ref_docs,
                )
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "당신은 에이텍(ATEC) 사내 보고서 전문 작성 어시스턴트입니다."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.4,
                    max_tokens=2048,
                )
                st.session_state.draft = response.choices[0].message.content
            except openai.AuthenticationError:
                st.error("API 키 인증 오류입니다. .env 파일의 OPENAI_API_KEY를 확인하세요.")
            except openai.RateLimitError:
                st.error("API 요청 한도를 초과했습니다. 잠시 후 다시 시도하세요.")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

# ────────────────────────── 초안 출력 ──────────────────────────
if st.session_state.draft:
    st.markdown("---")
    st.markdown("### 📝 생성된 보고서 초안")

    # 결재/합의 라인 미리보기
    ap_filled = [a for a in st.session_state.approval_line if a.strip()]
    cn_filled = [c for c in st.session_state.consensus_line if c.strip()]

    if ap_filled or cn_filled:
        st.markdown("**결재/합의 라인 미리보기**")
        preview_cols = st.columns(2)
        with preview_cols[0]:
            if ap_filled:
                st.markdown("✅ **결재 라인**")
                grid_html = '<div class="approval-grid" style="grid-template-columns: repeat(auto-fill, minmax(100px,1fr));">'
                for name in ap_filled:
                    grid_html += f'<div class="approval-cell"><div class="label">결재</div><div class="name">{name}</div></div>'
                grid_html += "</div>"
                st.markdown(grid_html, unsafe_allow_html=True)
        with preview_cols[1]:
            if cn_filled:
                st.markdown("🤝 **합의 라인**")
                grid_html = '<div class="approval-grid" style="grid-template-columns: repeat(auto-fill, minmax(100px,1fr));">'
                for name in cn_filled:
                    grid_html += f'<div class="approval-cell"><div class="label">합의</div><div class="name">{name}</div></div>'
                grid_html += "</div>"
                st.markdown(grid_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f'<div class="draft-box">{st.session_state.draft}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    dl_col, copy_col = st.columns([1, 1])
    with dl_col:
        st.download_button(
            label="📥 초안 텍스트 다운로드",
            data=st.session_state.draft.encode("utf-8"),
            file_name=f"에이텍_보고서_{report_date}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with copy_col:
        if st.button("🔄 초안 재생성", use_container_width=True):
            st.session_state.draft = ""
            st.rerun()
