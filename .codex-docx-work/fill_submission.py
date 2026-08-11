from copy import deepcopy
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from lxml import etree


WORK = Path(__file__).parent
SOURCE = WORK / "reference.docx"
OUTPUT = WORK.parent / "deliverables" / "AJOU_PBL_1차_MVP_쿠폰콕_통합제출서.docx"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = "{%s}" % NS["w"]
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def direct_rows(table):
    return table.findall(f"{W}tr")


def direct_cells(row):
    return row.findall(f"{W}tc")


def ensure_rows(table, count: int) -> None:
    rows = direct_rows(table)
    while len(rows) < count:
        clone = deepcopy(rows[-1])
        table.append(clone)
        rows = direct_rows(table)


def set_cell(tables, table_index: int, row_index: int, cell_index: int, text: str) -> None:
    table = tables[table_index]
    ensure_rows(table, row_index + 1)
    row = direct_rows(table)[row_index]
    cell = direct_cells(row)[cell_index]
    paragraphs = cell.findall(f"{W}p")
    if paragraphs:
        paragraph = paragraphs[0]
    else:
        paragraph = etree.Element(f"{W}p")
        cell.append(paragraph)

    paragraph_properties = paragraph.find(f"{W}pPr")
    first_run = paragraph.find(f".//{W}r")
    run_properties = deepcopy(first_run.find(f"{W}rPr")) if first_run is not None and first_run.find(f"{W}rPr") is not None else None

    for child in list(paragraph):
        if child is not paragraph_properties:
            paragraph.remove(child)

    run = etree.SubElement(paragraph, f"{W}r")
    if run_properties is not None:
        run.append(run_properties)
    lines = str(text).split("\n")
    for index, line in enumerate(lines):
        if index:
            etree.SubElement(run, f"{W}br")
        text_element = etree.SubElement(run, f"{W}t")
        text_element.set(XML_SPACE, "preserve")
        text_element.text = line

    for child in list(cell):
        if child.tag not in {f"{W}tcPr", f"{W}p"}:
            cell.remove(child)
    for extra_paragraph in cell.findall(f"{W}p")[1:]:
        cell.remove(extra_paragraph)


def set_row(tables, table_index: int, row_index: int, values: list[str]) -> None:
    ensure_rows(tables[table_index], row_index + 1)
    for cell_index, value in enumerate(values):
        set_cell(tables, table_index, row_index, cell_index, value)


def fill(document_xml: bytes) -> bytes:
    root = etree.fromstring(document_xml)
    tables = root.xpath("/w:document/w:body/w:tbl", namespaces=NS)
    if len(tables) != 87:
        raise RuntimeError(f"Expected 87 top-level tables, found {len(tables)}")

    # Cover metadata and submission checklist.
    cover = {
        1: ["프로젝트명", "쿠폰콕"],
        2: ["팀명", "쿠폰콕"],
        3: ["팀원", "김형우 / 기획·Flutter·FastAPI·ADK·GCP 풀스택 개발"],
        4: ["제출일", "2026-08-11"],
        5: ["GitHub 저장소", "https://github.com/guddn/Coupon_Kock"],
        6: ["배포 서비스", "Web: https://proj-aj25-211200020328.web.app\nAPI: https://coupon-kock-663890381698.asia-northeast3.run.app"],
    }
    for row_index, values in cover.items():
        set_row(tables, 1, row_index, values)
    for row_index in range(1, 7):
        set_cell(tables, 4, row_index, 0, "[✓]")

    # Section 01: one-page MVP summary.
    set_cell(tables, 6, 0, 0, "사용자가 등록한 유효 쿠폰과 현재 GPS 위치를 연결해, 쿠폰 사용 가능 주변 매장 Top 5와 예상 최저 결제금액을 근거와 함께 안내하는 위치 기반 혜택 에이전트")
    summary_rows = {
        1: ["해결할 문제", "모바일 쿠폰이 갤러리·메신저에 흩어져 사용 시점을 놓치고, 쿠폰·카드·통신사 조건을 결제 직전에 직접 비교하기 어렵다."],
        2: ["핵심 사용자/고객", "모바일 쿠폰과 여러 결제 혜택을 보유하지만 관리와 비교에 시간을 쓰기 어려운 대학생·직장인"],
        3: ["사용할 공공·산업 데이터", "소상공인시장진흥공단 상가(상권)정보 OpenAPI, Google Maps 위치·지도 데이터, 사용자 등록 쿠폰"],
        4: ["Gemini의 역할", "Google ADK가 매장 매칭·쿠폰 조회·근거 검색·가격 계산 Tool을 호출하도록 조정하고, 계산 결과를 바꾸지 않은 채 추천 이유를 설명"],
        5: ["RAG의 역할", "공식 카드·통신사 문서에서 유효한 혜택 규칙과 출처를 검색하는 후속 모듈. 1차 MVP에서는 no_evidence 안전 응답까지 구현"],
        6: ["MVP 핵심 기능", "쿠폰 수동 등록·Firestore 저장, 시작 시 위치 권한, 지도 현재 위치, 쿠폰 사용 가능 주변 매장 거리순 Top 5, 결정적 가격 계산, ADK Tool trace, Cloud Run/Firebase 배포"],
        7: ["검증할 핵심 가설", "공공데이터·쿠폰·GPS를 연결해 관련 매장을 좁히고, LLM과 결정적 계산을 분리하면 재현 가능한 추천 흐름을 만들 수 있다."],
        8: ["성공 판단 기준", "백엔드 16개·Flutter 5개 자동화 테스트 통과, 배포 URL/health 200, 무관 매장 제외 후 거리순 Top 5, 근거 없는 혜택 미적용"],
    }
    for row_index, values in summary_rows.items():
        set_row(tables, 7, row_index, values)
    set_cell(tables, 8, 0, 0, "기존 쿠폰 관리 앱은 쿠폰 저장·만료 알림 또는 결제수단 추천 중 일부 기능에 집중한다. 쿠폰콕은 ① 현재 위치와 보유 쿠폰을 먼저 결합해 후보 매장을 줄이고, ② 공공데이터 인증키를 서버에서만 사용하며, ③ 거리·할인 금액을 LLM이 아닌 결정적 코드로 계산한다. Gemini는 Tool 오케스트레이션과 근거 설명에 집중하고, 공식 출처가 없는 혜택은 계산하지 않는다.")

    # Section 02: evidence and problem framing.
    set_cell(tables, 10, 0, 0, "모바일 쿠폰은 보유 여부와 유효기간을 놓치기 쉽고, 카드·통신사 혜택은 서로 다른 앱과 문서에 분산되어 있다. 한국소비자원 조사에서 모바일 상품권 이용 경험자 500명 중 52.0%가 유효기간 만료 시까지 사용하지 못했고, 미사용자 중 63.5%는 별도 조치를 하지 않았다.\n\n1차 MVP는 전국 상가정보 OpenAPI로 현재 위치 반경의 업소를 조회하고, Firestore의 유효 쿠폰 브랜드와 일치하는 업소만 남겨 거리순 Top 5를 제공한다. 할인 금액은 결정적 calculator가 계산하고 Gemini는 결과와 불확실성을 설명한다. 다만 상가정보는 프랜차이즈 전체를 보장하는 브랜드 Store Master가 아니므로 Google Places 또는 공식 매장 데이터 보완이 필요하다.")
    set_row(tables, 11, 3, ["E3", "공공데이터", "공공데이터포털: 소상공인시장진흥공단 상가(상권)정보 API", "국세청·카드사 기반 전국 상호명·업종·주소·위경도 제공, 무료 OpenAPI", "GPS 기반 주변 업소 후보를 만들 수 있으나 브랜드 누락·동일 건물 좌표 중복을 품질 제약으로 관리해야 함"])
    set_cell(tables, 12, 0, 0, "모바일 쿠폰을 여러 장 보유한 사용자는 실제 결제 장소에서 보유 쿠폰과 카드·통신사 조건을 동시에 기억하고 비교하기 어렵다. 쿠폰은 이미지와 메신저에 분산되고 혜택 규칙은 여러 공식 문서에 흩어져 있으며, 적용 순서·중복·한도 계산까지 필요하기 때문이다. 위치와 유효 쿠폰을 연결하고 검증된 계산 결과를 제시하면 결제 직전 탐색 비용과 미사용 가능성을 줄일 수 있다.")
    set_cell(tables, 13, 0, 0, "[표면적 현상]\n- 쿠폰이 있어도 사용 가능한 매장과 유효기간을 놓친다.\n- 결제 직전 카드사·통신사 앱을 각각 열어본다.\n- 조건이 복잡하면 비교를 포기한다.\n\n[근본 원인]\n- 비정형 쿠폰 정보가 검색 가능한 데이터로 구조화되지 않음\n- GPS와 쿠폰 브랜드·매장 데이터가 연결되지 않음\n- 혜택 자연어 규칙과 결정적 계산 계층이 분리되지 않음\n\n[외부 제약]\n- 공공 상가데이터의 브랜드 누락·동일 좌표\n- 카드·통신사 정책 변경과 공식 문서 저작권\n- 전월 실적·잔여 한도 자동 조회 API 부재")

    # Section 03: users and requirements.
    set_cell(tables, 15, 4, 4, "중")
    requirement_status = {1: "Must / OCR 부분", 2: "Must / 포그라운드 완료", 3: "Must / 쿠폰 계산 완료", 4: "Should / RAG 후속"}
    for row_index, value in requirement_status.items():
        set_cell(tables, 17, row_index, 4, value)
    set_cell(tables, 18, 0, 0, "개발 과정에서 가정을 다음과 같이 변경했다.\n- 철도역·지역화폐 가맹점 중심 → 전국 상가정보 반경 API 중심으로 변경\n- 통합 자체를 차별점으로 설정 → 공식 근거, 결정적 계산, 개인정보 최소수집으로 변경\n- 앱 종료 상태 자동 알림 → 1차 MVP는 포그라운드 GPS와 지도 탐색으로 축소\n- 이미지 OCR 자동 등록 → 웹 MVP는 수동 등록으로 완결하고 Android 온디바이스 OCR을 후속으로 분리\n- 모든 카드·통신사 자동 비교 → 공식 문서 RAG가 없을 때 no_evidence를 반환하도록 안전하게 제한\n- 공공데이터가 모든 프랜차이즈를 포함한다고 가정 → Google Places/공식 매장 데이터 보완 필요를 확인")

    # Section 04: implemented solution.
    set_cell(tables, 20, 0, 0, "1) 입력: 사용자가 웹에서 쿠폰 브랜드·상품명·금액·유효기간을 등록하고 앱 시작 시 위치 권한을 허용한다.\n2) 처리: FastAPI가 쿠폰을 Firestore에 저장한다. 주변 탭은 GPS를 백엔드에 전달하고, 백엔드는 상가정보 OpenAPI를 조회한 뒤 만료되지 않은 쿠폰 브랜드와 일치하는 매장만 남긴다. 매장 좌표로 거리를 계산해 Top 5를 반환한다.\n3) 계산·Agent: deterministic calculator가 가능한 쿠폰 조합을 계산한다. Google ADK는 매장 매칭→쿠폰/프로필 조회→공식 근거 조회→가격 계산 Tool을 호출하고 tool_trace를 반환한다.\n4) 결과: Flutter가 현재 위치, 매장 마커, 거리순 목록과 추천 결과를 표시한다. RAG 근거가 없으면 임의 카드 할인을 만들지 않는다.")
    set_row(tables, 21, 1, ["정보 탐색", "갤러리·메신저·혜택 앱을 개별 확인", "GPS와 등록 쿠폰을 기준으로 관련 주변 매장만 표시", "후보를 한 화면의 거리순 Top 5로 축소"])
    set_row(tables, 21, 2, ["판단·분석", "조건과 할인 금액을 사용자가 직접 계산", "결정적 calculator가 조합을 계산하고 Gemini는 설명만 수행", "동일 입력에 동일 결과, LLM 산술 환각 방지"])
    set_row(tables, 21, 3, ["결과 활용", "혜택 적용 여부를 사용자가 다시 판단", "예상 결제금액·절감액·확인 조건·근거 상태 제공", "근거가 없으면 미적용하여 신뢰성 우선"])
    set_cell(tables, 22, 0, 0, "- 접근성: Firebase Hosting URL에서 별도 설치 없이 웹 데모 접근\n- 정확성: 거리와 할인 금액을 결정적 코드로 계산; 총 21개 자동화 테스트 통과\n- 신뢰성: 공식 source_id 없는 카드·통신사 규칙은 계산에 전달하지 않음\n- 개인정보: PIN·바코드·카드번호를 스키마에서 제외하고 정확한 위치는 비영구 처리\n- 운영성: health/API 문서, request_id·session_id·tool_trace 제공\n- 미측정: 정식 사용자 과업 시간과 RAG 검색 품질은 후속 평가 필요")
    set_cell(tables, 23, 0, 0, "1. 사용자가 스타벅스 등 모바일 쿠폰을 수동 등록한다.\n2. 쿠폰은 사용자 ID와 함께 Firestore에 저장된다.\n3. 주변 탭 진입 시 현재 GPS를 확인하고 반경 1km 상가정보를 조회한다.\n4. 만료 쿠폰을 제외하고 쿠폰 브랜드와 매장명이 일치하는 곳만 남긴다.\n5. 최신 위치에서 거리를 재계산해 가까운 순 Top 5를 지도와 목록에 표시한다.\n6. 10,000원 혜택 비교를 요청하면 calculator가 유효 쿠폰 조합의 최종 금액을 계산한다.\n7. ADK 엔드포인트는 Tool 호출 순서와 Gemini의 근거 설명을 반환한다.\n8. 공식 카드·통신사 RAG가 없는 상태에서는 해당 할인을 적용하지 않는다.")

    # Section 05: scope/status.
    feature_rows = {
        1: ["F-01", "쿠폰 등록·구조화", "쿠폰을 검색 가능한 데이터로 보관", "Must", "브랜드·상품·금액·유효기간 입력→Firestore 저장→목록 갱신", "부분 완료: 수동 등록 완료, OCR 후속"],
        2: ["F-02", "위치 기반 매장 Top 5", "현재 위치에서 쿠폰 사용 가능 매장 확인", "Must", "GPS→공공 API→쿠폰 필터→거리 정렬→지도/목록", "완료: 포그라운드, 팝업 후속"],
        3: ["F-03", "혜택 계산·ADK Agent", "예상 최저 결제금액과 이유 확인", "Must", "결정적 calculator 및 Tool trace, 근거 없으면 미적용", "부분 완료: 쿠폰 계산·Agent 완료, RAG 후속"],
        4: ["F-04", "쿠폰/프로필 관리", "등록 쿠폰 재사용", "Should", "쿠폰 등록·조회; 민감정보 미저장", "부분 완료: 쿠폰 완료, 카드·통신사 후속"],
    }
    for row_index, values in feature_rows.items():
        set_row(tables, 25, row_index, values)
    set_cell(tables, 26, 0, 0, "- Android 이미지 OCR 및 바코드/PIN 마스킹: 웹 MVP는 수동 입력으로 대체\n- 앱 종료 상태 geofencing·푸시 알림: 권한·배터리·플랫폼 정책 검증 후 구현\n- 카드사 계정 연동과 전월 실적·잔여 한도 자동 조회: 공개 API 부재\n- 실제 결제·바코드 사용 처리: 추천까지만 제공\n- 전체 프랜차이즈 Store Master: 상가정보 누락을 Google Places/공식 매장 데이터로 보완 예정\n- 운영용 카드·통신사 RAG: 문서 수집 권한·평가셋 확보 후 연결")
    nfr_rows = {
        1: ["성능", "주변 매장/추천 API 응답", "Cloud Run 호출 및 브라우저 확인", "health 및 주요 API 200 확인; cold start 수치 측정은 후속"],
        2: ["정확성", "쿠폰 필터·거리 정렬·가격 계산", "pytest 16개 + Flutter 5개", "21개 자동화 테스트 통과; 사용자·RAG 정확도는 미측정"],
        3: ["보안·개인정보", "비밀키·PIN·카드번호·위치 최소수집", "요청 스키마·Firestore·Secret 점검", "공공 API 키는 Secret Manager, PIN/카드번호 필드 없음, ADK 세션 즉시 삭제"],
        4: ["사용성·접근성", "쿠폰 등록→지도→추천 흐름", "Flutter Web 수동 QA", "Firebase Hosting에서 흐름 확인; 정식 3~5명 테스트 미실시"],
        5: ["운영성", "배포·오류 추적·문서화", "Cloud Build/Run 로그, README, Swagger", "health/docs/tool_trace 제공; Cloud Trace 세부 span은 후속"],
    }
    for row_index, values in nfr_rows.items():
        set_row(tables, 27, row_index, values)
    set_cell(tables, 28, 0, 0, "H1. GPS와 보유 쿠폰을 함께 사용하면 주변의 무관한 매장을 제거하고 실제 사용 가능한 후보를 거리순으로 제시할 수 있다.\n- 결과: 필터→정렬→Top 5 파이프라인 자동화 테스트 통과. 기술 가설은 지지됨.\n- 추가 검증: 실제 사용자 3~5명의 탐색 시간·과업 성공률 비교 필요.\n\nH2. LLM과 결정적 calculator를 분리하면 할인 계산의 재현성을 확보할 수 있다.\n- 결과: calculator 및 API 테스트 통과, 모델이 결과를 변경하지 않도록 instruction 적용. 기술 가설은 지지됨.\n- 추가 검증: 공식 혜택 RAG 연결 후 검색 근거 Top-5와 최종 추천 정확도를 별도 평가해야 함.")

    # Section 06: architecture and API.
    architecture_rows = {
        1: ["Frontend", "Flutter Web/Android", "위치 권한, 지도, 쿠폰 등록·목록, 주변 매장·추천 표시", "사용자 입력·GPS", "HTTPS API 요청·화면"],
        2: ["Backend API", "FastAPI on Cloud Run", "검증, 쿠폰/매장/추천 API, 외부 API 보호", "JSON·좌표", "Pydantic 응답/오류"],
        3: ["Agent", "Google ADK 2.6.3 + Gemini 2.5 Flash", "Tool 오케스트레이션과 근거 설명", "정형 요청·Tool 결과", "answer·tool_trace"],
        4: ["Data", "Firestore + 공공데이터 OpenAPI", "쿠폰 영속화와 반경 상가 후보 조회", "쿠폰·좌표", "유효 쿠폰·주변 매장"],
        5: ["Infra", "Firebase Hosting·Cloud Build·Artifact Registry·Secret Manager", "웹 호스팅, 이미지 빌드, Cloud Run 배포, 비밀값 주입", "Git commit·Secret", "배포 URL·Revision"],
    }
    for row_index, values in architecture_rows.items():
        set_row(tables, 31, row_index, values)
    api_rows = [
        ["GET", "/health", "상태 확인", "-", "200 {status: ok}"],
        ["POST", "/api/coupons", "쿠폰 등록", "user_id·brand·상품·금액·유효기간", "201 RegisteredCoupon / 422"],
        ["GET", "/api/coupons", "사용자 쿠폰 조회", "user_id", "200 쿠폰 목록"],
        ["GET", "/api/stores/nearby", "쿠폰 사용 가능 Top 5", "user_id·위경도·반경·limit", "200 stores·data_source·notice"],
        ["POST", "/api/recommendations", "결정적 가격 추천", "user_id·위경도·결제금액", "200 후보·추천·조건 / 404"],
        ["GET", "/api/agent", "ADK 정보", "-", "모델·Tool·실행 endpoint"],
        ["POST", "/api/agent/recommendations", "ADK 추천 실행", "사용자·위치·금액·선택 매장", "answer·tool_trace / 503"],
        ["POST", "/api/coupons/parse", "OCR 텍스트 구조화 스캐폴드", "마스킹된 텍스트", "Coupon·confidence·needs_review"],
    ]
    ensure_rows(tables[32], len(api_rows) + 1)
    for index, values in enumerate(api_rows, start=1):
        set_row(tables, 32, index, values)

    # Section 07: data and model.
    data_rows = {
        1: ["상가(상권)정보 OpenAPI", "소상공인시장진흥공단", "Cloud Run에서 반경 실시간 호출", "상가업소번호·상호·업종·주소·위경도", "브랜드 누락, 동일 건물 좌표, 갱신 지연", "공공데이터포털 이용허락범위 제한 없음"],
        2: ["쿠폰 데이터", "사용자 입력 / Cloud Firestore", "등록 시 저장, 조회 시 유효기간 필터", "coupon_id·user_id·brand·상품·금액·expiry", "수동 오입력, 인증 전 demo-user 공유", "개인정보 최소수집·서비스 내부 데이터"],
        3: ["카드·통신사 공식 문서", "카드사·통신사 공식 채널", "후속 수집·갱신 예정", "source_id·제목·URL·유효기간·규칙", "최신성·저작권·상품별 예외", "원문 재배포 금지, 허용 범위 확인 후 색인"],
    }
    for row_index, values in data_rows.items():
        set_row(tables, 34, row_index, values)
    set_cell(tables, 35, 0, 0, "- 좌표 범위: 위도 -90~90, 경도 -180~180; 반경 100~5,000m, limit 1~20 검증\n- 매장명/브랜드: 공백·특수문자·대소문자 정규화 후 보수적 부분 일치\n- 거리: Haversine으로 재계산하고 오름차순 정렬; 동률은 프론트에서 매장명 순\n- 쿠폰: 사용자별 조회 후 UTC 기준 만료일이 오늘 이상인 항목만 사용\n- 금액: 0~10,000,000원 범위 검증; 여러 쿠폰 임의 합산 금지\n- 외부 API 실패: fixture와 notice를 분리해 실제 데이터로 오인하지 않게 표시")
    set_cell(tables, 36, 0, 0, "users/{user_id}\n └─ coupons/{coupon_id}: brand, product_name, coupon_type, face_value, expiry_date, created_at\n\n외부 NearbyStore(비영구): store_id, name, category, address, latitude, longitude, distance_m\nADK 실행(임시): request_id, session_id, answer, tool_trace → 응답 후 세션 삭제\n후속 benefit_sources: source_id, title, url, valid_from/to, embedding, structured_rule")
    risk_rows = {
        1: ["개인정보/민감정보 포함", "예(위치·쿠폰)", "PIN·바코드·카드번호 미수집, 정확한 위치 비영구, ADK 임시 세션 삭제"],
        2: ["출처·라이선스 제한", "예", "공공데이터 출처 표기, 카드·통신사 문서는 원문 재배포 대신 링크·허용 범위 확인"],
        3: ["편향 또는 대표성 부족", "예", "상가정보 브랜드 누락을 고지하고 Google Places/공식 Store Master 보완"],
        4: ["최신성·품질 불확실", "예", "응답 data_source·notice 표시, 좌표/유효기간 검증, 공식 문서 valid_to 관리"],
    }
    for row_index, values in risk_rows.items():
        set_row(tables, 37, row_index, values)

    # Section 08: Gemini and prompt.
    set_row(tables, 39, 1, ["ADK 혜택 추천", "gemini-2.5-flash, temperature 0.1, max 1,024 tokens", "user_id·위치·결제금액 + Tool 결과", "한국어 설명 + tool_trace", "거리·금액·쿠폰 유효성은 Python Tool이 결정; 모델은 재계산 금지"])
    set_row(tables, 39, 2, ["쿠폰 텍스트 구조화", "1차 MVP placeholder parser", "마스킹된 OCR 텍스트", "Coupon JSON + confidence + needs_review", "이미지 OCR·Vertex adapter는 후속; 12자리 이상 숫자 토큰 차단"])
    set_cell(tables, 40, 0, 0, "역할: 위치 기반 쿠폰·혜택 추천 서비스 ‘쿠폰콕’의 ADK 에이전트.\n순서: 입력 JSON 검증 → match_nearby_store → load_user_benefit_context → retrieve_official_benefit_rules → calculate_discount_options.\n규칙: 가장 큰 활성 쿠폰 한 장만 선택하고, 공식 source_id가 있는 카드 규칙만 계산에 전달한다. calculator의 recommended_option을 변경하거나 직접 산술 계산하지 않는다.\n안전: 카드번호·쿠폰 PIN·정확한 위치를 답변에 반복하지 않는다. 근거가 없으면 RAG 미연결 상태를 명시하고 혜택을 만들지 않는다.\n출력: 추천 옵션·예상 결제금액·절감액, 적용 구성, 확인 조건, 근거 상태를 간결한 한국어로 작성한다.")
    prompt_tests = {
        1: ["P-01", "유효 쿠폰·위치·10,000원", "Tool 순서대로 호출 후 calculator 결과 설명", "called/completed trace와 한국어 answer 반환", "통과"],
        2: ["P-02", "공식 카드 근거 없음", "임의 할인을 만들지 않고 no_evidence 표시", "rules/sources 빈 상태를 유지하고 쿠폰 또는 무혜택 계산", "통과"],
        3: ["P-03", "범위 밖 좌표·비정상 금액", "스키마 또는 Tool에서 차단", "422 또는 invalid_location/invalid_amount", "통과"],
    }
    for row_index, values in prompt_tests.items():
        set_row(tables, 41, row_index, values)
    set_cell(tables, 42, 0, 0, "- 환각: Tool 결과에 없는 매장·혜택·조건 생성 금지, 공식 source_id 없는 카드 규칙 미적용\n- 산술 오류: 금액은 deterministic calculator만 계산하고 Gemini가 변경하지 못하도록 instruction 고정\n- 입력 오류: Pydantic 범위 검증과 Tool 상태 코드로 차단\n- 외부 API 실패: 공공데이터는 fixture+notice, ADK 모델 실패는 503 반환\n- 개인정보: 정확한 위치를 최종 답변에 반복하지 않고 세션을 요청 후 삭제\n- 파싱 실패: 빈 최종 응답은 AgentExecutionError로 처리")

    # Section 09: honest RAG design/status.
    rag_rows = {
        1: ["지식 문서 범위", "KB카드 등 공식 카드 상품·통신사 멤버십 혜택 문서(후속)", "상품·브랜드·유효기간·중복 조건 질문에 한정"],
        2: ["문서 정제", "제목·URL·유효기간·대상·한도·제외 조건 구조화", "중복 제거, 출처 URL과 스냅샷 시점 검증"],
        3: ["Chunk 전략", "혜택 항목/표 행 단위, 의미 경계 우선; overlap 소량", "긴 페이지 단순 고정 분할보다 규칙 완결성 우선"],
        4: ["Embedding/Vector Store", "Firestore Vector Search + 임베딩 모델(후속)", "쿠폰/프로필과 같은 GCP 경계, metadata filter 지원"],
        5: ["검색 방식", "provider·card_product·merchant·valid_at filter + Top 5", "관련성보다 유효기간·상품 일치 필터를 먼저 적용"],
        6: ["재정렬/후처리", "source_id·유효기간·eligibility 검증 후 rule validator", "근거 없는 수치가 calculator에 들어가는 것을 차단"],
        7: ["출처 표시", "문서명·공식 URL·유효기간·source_id", "사용자가 추천 조건을 직접 재확인 가능"],
    }
    for row_index, values in rag_rows.items():
        set_row(tables, 44, row_index, values)
    set_cell(tables, 45, 0, 0, "RAG 처리 흐름(설계): 공식 문서 수집·권한 확인 → 혜택 단위 정제·메타데이터 → 임베딩·Vector Store → 사용자 카드/통신사·매장·날짜 필터 → Top 5 → rule validator → calculator → Gemini 출처 설명.\n\n현재 상태: retrieve_official_benefit_rules Tool 인터페이스와 no_evidence 안전 응답까지 구현. 실제 문서 수집·임베딩·Vector Search·검색 품질 평가는 후속 단계이다.")
    rag_eval_rows = [
        ["Q1 스타벅스 카드 할인", "공식 상품별 할인율·한도·실적", "미색인", "미평가", "KB카드 공식 문서 수집 후 평가"],
        ["Q2 쿠폰+카드 중복", "중복 가능 여부와 적용 순서", "미색인", "미평가", "rule schema와 정답셋 작성"],
        ["Q3 전월 실적 미충족", "자격 확인 필요 표시", "미색인", "미평가", "eligibility fixture 추가"],
        ["Q4 월 할인 한도", "잔여 한도 미연동 고지", "미색인", "미평가", "사용자 확인 흐름 설계"],
        ["Q5 유효기간 경과 문서", "검색·계산에서 제외", "미색인", "미평가", "valid_to metadata filter 테스트"],
    ]
    for row_index, values in enumerate(rag_eval_rows, start=1):
        set_row(tables, 46, row_index, values)

    # Sections 10-11: plan, review, change management.
    work_rows = [
        ["T-01", "저장소·환경·문서", "김형우", "-", "Flutter/FastAPI 실행·README", "완료"],
        ["T-02", "공공데이터·Firestore", "김형우", "T-01", "쿠폰 저장·주변 API 응답", "완료"],
        ["T-03", "Gemini/ADK/RAG", "김형우", "T-02", "Tool trace·안전 응답", "부분: ADK 완료, RAG 후속"],
        ["T-04", "Backend API", "김형우", "T-02/03", "Swagger·테스트·Cloud Run", "완료"],
        ["T-05", "Flutter Web UI", "김형우", "T-04", "쿠폰·지도·추천 흐름", "완료"],
        ["T-06", "배포·검증", "김형우", "T-04/05", "URL·health·21 tests", "완료 / 최신 commit 재배포 확인"],
    ]
    for row_index, values in enumerate(work_rows, start=1):
        set_row(tables, 48, row_index, values)
    standards = {
        1: ["저장소·브랜치", "GitHub main, 기능 단위 commit; 배포 전 git diff/status 확인"],
        2: ["개발 환경", "Flutter/Dart, Python 3.11, FastAPI, google-adk 2.6.3; Bash 기준 실행"],
        3: ["환경 변수", ".env.example에는 이름만 기록; API 키는 Secret Manager·dart-define, 실제 값 커밋 금지"],
        4: ["코드 품질", "Ruff, pytest, dart format, flutter analyze/test; 결정적 계산과 LLM 책임 분리"],
        5: ["협업 도구", "개인 프로젝트: GitHub commit 이력, README/docs, Cloud Build/Run 로그로 변경 추적"],
    }
    for row_index, values in standards.items():
        set_row(tables, 49, row_index, values)
    set_cell(tables, 50, 0, 0, "가장 큰 기술 위험은 ① 공공데이터의 브랜드 누락·동일 좌표·인증키 오류, ② GCP 사용자/빌드/런타임 서비스 계정의 IAM 혼동, ③ 공식 혜택 문서의 최신성·저작권, ④ LLM의 수치 환각이었다. 공공데이터는 data_source/notice와 Google Places 보완 계획으로, IAM은 주체별 최소 역할로, 혜택은 source_id·valid_to 필터로, 수치는 deterministic calculator로 대응했다.")
    progress_rows = {
        1: ["기획·설계", "문제·사용자·데이터·ADK Tool·Cloud 구조 정의", "4일 안에 OCR·RAG·알림까지 모두 구현하기 어려움", "핵심 GPS→쿠폰→매장→계산 흐름 우선", "김형우"],
        2: ["핵심 기능 구현", "쿠폰 API/Firestore, GPS, 지도, 공공데이터, calculator, ADK", "공공 API 키·브랜드 데이터 품질", "Secret Manager와 실패 notice, 브랜드 필터 도입", "김형우"],
        3: ["배포·검증", "Cloud Run·Firebase Hosting, health/API 200, 테스트", "Developer Connect·Secret IAM·Docker context", "계정/서비스 계정 분리 점검, Linux 경로 수정", "김형우"],
        4: ["시연·회고", "주변 매장 Top 5·tool_trace·한계 문서화", "지도 잘림·동일 좌표·프랜차이즈 누락", "탭 활성 후 지도 생성, 거리 재계산, 데이터 보완 백로그", "김형우"],
    }
    for row_index, values in progress_rows.items():
        set_row(tables, 52, row_index, values)
    review_rows = {
        1: ["구조·책임 분리", "Flutter·FastAPI·ADK·calculator 책임 혼재 위험", "거리/금액은 결정적 서비스, Gemini는 Tool·설명으로 분리", "[✓]"],
        2: ["오류·예외 처리", "외부 API/모델 실패 시 UI 오인 가능", "HTTP 검증, fixture notice, 503/404, 재시도 메시지", "[✓]"],
        3: ["키·개인정보·보안", "공공 키와 사용자 위치 노출 위험", "Secret Manager, 서버 호출, PIN/카드번호 제외, 임시 세션", "[✓]"],
        4: ["프롬프트/RAG 품질", "근거 없는 할인 생성 위험", "source_id 없는 규칙 미적용; RAG 미연결 명시", "[✓/RAG 후속]"],
        5: ["재현성·문서화", "로컬/Cloud 경로·계정 차이", "Bash 명령·README·API docs·테스트로 재현 절차 기록", "[✓]"],
    }
    for row_index, values in review_rows.items():
        set_row(tables, 53, row_index, values)
    set_cell(tables, 54, 0, 0, "주요 변경 결정\n1. 서비스명을 Coupon Knock에서 ‘쿠폰콕’으로 통일.\n2. 소스 업로드 방식에서 GitHub→Cloud Build→Cloud Run 트리거 방식으로 변경.\n3. 모든 주변 상가 표시에서 ‘보유 유효 쿠폰 브랜드와 일치하는 매장만’ 표시로 변경.\n4. 서버 distance_m만 표시하던 방식에서 Flutter가 최신 GPS로 거리를 재계산하도록 보강.\n5. 숨겨진 IndexedStack에서 지도를 미리 생성하던 구조를 탭 활성 후 생성으로 변경.\n6. OCR·운영 RAG·백그라운드 알림은 1차 MVP에서 부분 구현/후속으로 명시.")

    # Section 12: deployment.
    deploy_rows = {
        1: ["웹 인터페이스", "Flutter Web release → Firebase Hosting; 홈·주변·쿠폰·마이 탭"],
        2: ["백엔드 서비스", "Cloud Run coupon-kock, asia-northeast3, https://coupon-kock-663890381698.asia-northeast3.run.app"],
        3: ["데이터/저장소", "Cloud Firestore 쿠폰 저장, 공공데이터 OpenAPI 실시간 반경 조회"],
        4: ["환경 변수/Secret", "COUPON_STORAGE_BACKEND·GCP_PROJECT_ID는 Cloud Run env, PUBLIC_DATA_SERVICE_KEY는 Secret Manager; Maps 키는 build define"],
        5: ["빌드·배포 명령", "GitHub push→Cloud Build trigger→Artifact Registry→Cloud Run; flutter build web→firebase deploy"],
        6: ["헬스 체크", "GET /health가 HTTP 200 및 status=ok"],
        7: ["로그·모니터링", "Cloud Run Logs/Cloud Build history, API request_id·ADK tool_trace; Cloud Trace 세부 span은 후속"],
        8: ["비용·한도", "Cloud Run/Firestore/Firebase/Vertex/Maps 무료·과금 한도 내 MVP 운영; 공공 API 개발 10,000건/일, 운영 전 쿼터 확인"],
    }
    for row_index, values in deploy_rows.items():
        set_row(tables, 56, row_index, values)
    set_cell(tables, 57, 0, 0, "브라우저 → Firebase Hosting(Flutter Web) → HTTPS → Cloud Run(FastAPI/ADK)\nCloud Run → Firestore(쿠폰) / 공공데이터 OpenAPI(주변 상가) / Vertex AI Gemini(Agent)\nSecret Manager → Cloud Run 런타임 서비스 계정\nGitHub main → Developer Connect·Cloud Build → Artifact Registry → Cloud Run Revision")
    deployment_checks = {
        1: ["배포 URL 접근", "성공", "Firebase Hosting·Cloud Run URL 및 health 200 확인"],
        2: ["환경 변수·Secret 노출 없음", "확인", "Git diff/README 점검, Secret은 이름만 기록하고 실제 값 미기재"],
        3: ["오류 로그 확인 가능", "확인", "Cloud Run Logs와 Cloud Build 실행 로그에서 Revision/step 확인"],
        4: ["재배포 후 동작", "부분 확인", "배포 기능 200 확인; 로컬 최신 ddd365f는 push·재배포 후 최종 확인 필요"],
        5: ["README 실행·배포 안내 일치", "확인", "backend/frontend 실행, API·Secret·공공데이터 절차 기록"],
    }
    for row_index, values in deployment_checks.items():
        set_row(tables, 58, row_index, values)

    # Section 13: verification and user test status.
    test_rows = [
        ["TC-01", "쿠폰 등록→주변 Top 5", "유효 브랜드 쿠폰 등록 후 GPS/주변 API", "일치 매장만 거리순 최대 5개", "필터·정렬·limit 테스트 통과", "Pass"],
        ["TC-02", "입력 범위 오류", "반경 10,000m 또는 잘못된 좌표", "422로 차단", "FastAPI 검증 테스트 통과", "Pass"],
        ["TC-03", "공공 API 키/호출 실패", "키 없음 또는 외부 오류", "fixture+notice로 데이터 출처 표시", "오류 시 샘플 안내 확인", "Pass"],
        ["TC-04", "공식 혜택 근거 부족", "RAG rules/sources 없음", "임의 카드 할인 미적용", "no_evidence 유지 및 calculator 실행", "Pass"],
        ["TC-05", "Flutter Web 지도/거리", "위치 권한 후 주변 탭 진입", "전체 크기 지도·최신 거리 정렬", "정적 분석/테스트 통과; 배포 화면 재확인 필요", "Partial"],
    ]
    for row_index, values in enumerate(test_rows, start=1):
        set_row(tables, 60, row_index, values)
    user_rows = [
        ["U1 개발자 자체 QA", "쿠폰 등록→주변→추천", "공공 API·Firestore·지도 연결 확인", "지도 잘림·거리 동률·브랜드 누락 발견", "지도 지연 생성, 거리 재계산, 데이터 보완"],
        ["U2 외부 사용자", "미실시", "정식 3~5명 과업 테스트 미실시", "피드백 미수집", "후속 테스트 모집"],
        ["U3 외부 사용자", "미실시", "정량 시간·만족도 미측정", "피드백 미수집", "비교 과업과 설문 설계"],
    ]
    for row_index, values in enumerate(user_rows, start=1):
        set_row(tables, 61, row_index, values)
    metric_rows = {
        1: ["자동화 테스트", "pytest·flutter test", "전체 통과", "Backend 16 + Flutter 5 = 21 통과", "달성"],
        2: ["응답 시간", "Cloud Run 반복 측정", "중앙값 5초 이하", "정식 반복 측정 미실시", "미측정"],
        3: ["답변 근거성/정확성", "계산 fixture·RAG 정답셋", "calculator 100%, RAG Top-5 80%", "계산/API 테스트 통과; RAG 미연결", "부분"],
        4: ["사용 만족/이해도", "3~5명 과업·설문", "과업 성공 80%", "외부 사용자 테스트 미실시", "미측정"],
    }
    for row_index, values in metric_rows.items():
        set_row(tables, 62, row_index, values)
    set_cell(tables, 63, 0, 0, "기술 가설은 부분적으로 지지되었다. 등록 쿠폰과 GPS, 공공 상가데이터를 연결해 무관 매장을 제거하고 거리순 Top 5를 반환하는 흐름과 결정적 가격 계산은 자동화 테스트로 확인했다. Cloud Run과 Firebase Hosting 배포 및 주요 API 200도 확인했다. 다만 공공데이터의 프랜차이즈 완전성, 공식 혜택 RAG 검색 정확도, 실제 사용자의 탐색 시간·만족도는 검증하지 못했으므로 최종 사용자 가치 가설은 후속 실험이 필요하다.")

    # Section 14: improvements and final state.
    improvement_rows = [
        ["I-01", "Cloud Build 소스·context 실패", "Developer Connect 403, Backend path 오류", "빌드 계정 권한 및 Linux 대소문자 backend 경로 수정", "소스 fetch·Docker build 성공", "완료"],
        ["I-02", "Cloud Run Secret 접근 실패", "Revision secretAccessor 오류", "실제 런타임 서비스 계정에 Secret 단위 역할 부여", "Revision 생성 및 Secret 주입", "완료"],
        ["I-03", "무관한 주변 매장·거리 정렬", "화면 QA·API 응답", "유효 쿠폰 브랜드 필터 후 거리 정렬·Top 5, 최신 GPS 재계산", "후보 정확도와 순서 개선", "완료"],
        ["I-04", "Flutter Web 지도 잘림", "IndexedStack 숨김 상태 초기화", "주변 탭 활성 후 Map 생성, SizedBox.expand·bounds 적용", "전체 영역 표시 구조로 변경", "완료/재배포 확인"],
    ]
    for row_index, values in enumerate(improvement_rows, start=1):
        set_row(tables, 65, row_index, values)
    final_state = {
        1: ["정상 시연 가능한 기능", "쿠폰 수동 등록·Firestore 조회, 앱 시작 GPS 권한, 현재 위치 지도, 공공데이터 주변 조회, 쿠폰 필터·거리순 Top 5, 결정적 추천 API, ADK 정보·tool_trace"],
        2: ["부분 구현/제한 기능", "쿠폰 parser는 placeholder, Agent는 공식 RAG 없이 no_evidence, demo-user 고정, 포그라운드 위치만 지원"],
        3: ["미구현 기능", "이미지 OCR, 카드·통신사 Vector RAG, Firebase Auth, 백그라운드 geofencing/푸시, 쿠폰 사용 완료 상태"],
        4: ["알려진 오류", "공공 상가정보에 스타벅스 등 일부 브랜드 누락·동일 건물 좌표가 존재; 최신 지도 패치는 재배포 확인 필요"],
        5: ["운영 시 주의사항", "Secret/Maps 키 제한, API 쿼터·Cloud 비용, 공식 혜택 최신성·저작권, demo-user 데이터 분리, 데이터 출처 notice 확인"],
    }
    for row_index, values in final_state.items():
        set_row(tables, 66, row_index, values)
    set_cell(tables, 67, 0, 0, "대표 화면\n1. 쿠폰 등록/목록: 브랜드·상품명·금액·유효기간 입력 후 Firestore 저장\n2. 주변: 현재 위치 Google Map + 쿠폰 사용 가능 매장 거리순 Top 5\n3. 홈 추천: 10,000원 기준 쿠폰 적용 예상 결제금액\n\n제출 전 확인: 최신 commit을 Firebase/Cloud Run에 재배포한 뒤 주변 화면과 Swagger 응답 캡처 2~4장을 이 영역에 추가한다.")

    # Section 15: demo and presentation.
    presentation_rows = [
        ["1", "문제와 고객", "쿠폰을 보유해도 사용 시점과 최적 혜택을 놓친다", "김형우", "1분"],
        ["2", "솔루션과 MVP 범위", "GPS·유효 쿠폰·주변 매장을 연결한 완결 흐름", "김형우", "1분"],
        ["3", "데이터·Gemini·RAG·아키텍처", "공공데이터+결정적 계산+ADK, RAG는 안전 스캐폴드", "김형우", "2분"],
        ["4", "실서비스 시연", "쿠폰 등록→주변 Top 5→추천/tool trace", "김형우", "2분"],
        ["5", "검증 결과와 한계", "21 tests·배포 성공, 브랜드 데이터·RAG·사용자 검증 한계", "김형우", "1분"],
        ["6", "고도화 계획", "Places·OCR·RAG·Auth·geofencing 순으로 확장", "김형우", "1분"],
    ]
    for row_index, values in enumerate(presentation_rows, start=1):
        set_row(tables, 69, row_index, values)
    set_cell(tables, 70, 0, 0, "시연 전: Firebase/Cloud Run health, 위치 권한, demo-user 쿠폰, Maps 키·공공 API를 확인한다.\n1) 쿠폰 탭에서 브랜드·금액·유효기간 등록 → 목록 갱신 확인\n2) 주변 탭에서 위치 권한 허용 → 현재 위치와 쿠폰 사용 가능 Top 5 확인\n3) 매장을 눌러 지도 이동·거리 순서 확인\n4) 홈에서 10,000원 혜택 비교 → 예상 결제금액 확인\n5) /api/agent/recommendations 응답의 answer·tool_trace 설명\n실패 대비: 미리 저장한 API JSON, 지도 화면, Swagger 화면을 사용하고 public API fixture notice를 설명한다.")
    set_cell(tables, 71, 0, 0, "- Flutter: Android/Web 단일 코드베이스와 Google Maps·GPS 패키지 활용\n- FastAPI/Pydantic: 짧은 MVP에서 명확한 JSON 계약·Swagger·비동기 API 제공\n- Cloud Run: 컨테이너 기반 자동 확장과 GitHub/Cloud Build 배포\n- Firestore: 서버리스 쿠폰 저장 및 향후 Vector Search 확장 경로\n- Google ADK/Gemini: Tool 호출 순서와 설명을 분리하고 tool_trace 제공\n- 결정적 Python calculator: 금액·거리의 재현성과 테스트 가능성 확보\n- 공공데이터 OpenAPI: 전국 상가 후보를 무료·공식 데이터로 조회\n대안: Firebase Functions 대신 FastAPI/Cloud Run을 선택해 ADK·Python 데이터 로직과 Docker 배포를 단일 서비스로 유지했다.")
    set_cell(tables, 72, 0, 0, "Q. 왜 LLM이 직접 할인 금액을 계산하지 않나?\nA. 수치 환각을 방지하기 위해 calculator 결과만 사용하고 Gemini는 설명을 담당한다.\n\nQ. 스타벅스가 검색되지 않으면 서비스가 실패한 것 아닌가?\nA. 상가정보는 브랜드 전체를 보장하지 않는다. Google Places Text Search/공식 매장 데이터로 보완할 계획이다.\n\nQ. 카드 혜택 근거는 신뢰할 수 있나?\nA. 현재 RAG는 미연결이며 no_evidence를 반환한다. 운영에서는 공식 URL·유효기간·source_id가 있는 규칙만 계산한다.\n\nQ. 개인정보는 어떻게 보호하나?\nA. PIN·바코드·카드번호를 수집하지 않고 위치는 비영구 처리하며 Secret은 서버에만 둔다.\n\nQ. 비용과 확장성은?\nA. Cloud Run/Firestore 자동 확장을 사용하되 Maps·Vertex·공공 API 쿼터와 캐시 정책을 운영 전에 설정한다.")

    # Section 16: feedback and backlog.
    feedback_rows = {
        1: ["사용자", "무관한 주변 매장 제외, 지도 잘림과 거리 정렬 개선 요청", "후보 정확도와 지도 가독성이 핵심 신뢰 요소", "반영: 쿠폰 필터·탭 활성 지도·거리 재계산"],
        2: ["동료 팀", "정식 피드백 미수집", "발표 전 동료 리뷰 필요", "보류: 시연 리허설에서 수집"],
        3: ["강사/리뷰어", "정식 피드백 미수집", "RAG·사용자 검증 항목을 객관적으로 확인 필요", "보류: 제출 후 반영"],
        4: ["팀 자체 회고", "공공데이터 호출 성공만으로 브랜드 완전성을 가정함", "데이터 품질·브랜드 식별이 Agent 품질의 선행 조건", "반영: Places/공식 Store Master 백로그"],
    }
    for row_index, values in feedback_rows.items():
        set_row(tables, 74, row_index, values)
    backlog_rows = [
        ["B-01", "Google Places/공식 매장 데이터 보완", "프랜차이즈 누락 감소", "중", "1", "스타벅스 등 5개 브랜드 반경 정답셋 정확도"],
        ["B-02", "Firebase Authentication", "사용자 쿠폰 데이터 분리", "중", "2", "UID별 CRUD·권한 테스트"],
        ["B-03", "Android 온디바이스 OCR", "쿠폰 등록 시간 단축", "중", "3", "대표 이미지 20장 필드 추출률"],
        ["B-04", "공식 카드·통신사 RAG", "근거 기반 혜택 확장", "상", "4", "5개 질의 Top-5·최종 추천 평가"],
        ["B-05", "Geofencing·푸시 알림", "매장 진입 시점 자동 추천", "상", "5", "배터리·권한·오탐·사용자 방해도 테스트"],
    ]
    for row_index, values in enumerate(backlog_rows, start=1):
        set_row(tables, 75, row_index, values)
    set_cell(tables, 76, 0, 0, "후반기 목표는 ‘쿠폰을 등록한 사용자가 실제 브랜드 매장 근처에서 5초 안에 신뢰 가능한 추천을 확인한다’로 정의한다. 대표 브랜드 5개에 대해 매장 매칭 정확도 90% 이상, OCR 필수 필드 추출률 90% 이상, calculator 100%, RAG 핵심 근거 Top-5 80% 이상, 사용자 과업 성공률 80% 이상을 측정한다.")
    set_cell(tables, 77, 0, 0, "Keep\n- LLM과 거리·금액 계산 책임 분리\n- Secret Manager와 개인정보 최소수집\n- 작은 기능 단위 테스트·배포 로그 확인\n\nProblem\n- IAM 주체와 배포 흐름 이해에 시간 소요\n- 공공데이터 브랜드 누락·동일 좌표를 늦게 확인\n- 4일 범위에 OCR·RAG·알림을 과도하게 포함\n\nTry\n- 먼저 데이터 coverage·정답셋 spike 수행\n- 사용자/빌드/런타임 서비스 계정 IAM 표준화\n- 구현/부분/미구현 상태를 매일 문서에 동기화\n- RAG 검색 평가와 사용자 과업 테스트를 기능 개발과 병행")

    # Sections 17-18: artifacts, sources, reproduction, checklist.
    artifact_rows = [
        ["GitHub 저장소", "https://github.com/guddn/Coupon_Kock", "공개", "문서 작성 시 로컬 HEAD ddd365f; push 후 원격 확인"],
        ["배포 서비스", "https://proj-aj25-211200020328.web.app", "공개", "Firebase Hosting 접속 확인"],
        ["API 문서", "https://coupon-kock-663890381698.asia-northeast3.run.app/docs", "공개", "FastAPI Swagger"],
        ["발표 자료", "별도 작성 예정", "미제출", "본 통합 문서를 기반으로 제작"],
        ["시연 영상", "미촬영", "미제출", "최신 재배포 후 녹화 예정"],
        ["기타 산출물", "README.md, docs/architecture.md, docs/api.md, docs/public-data.md", "공개", "실행·아키텍처·API·데이터 문서"],
    ]
    for row_index, values in enumerate(artifact_rows, start=1):
        set_row(tables, 79, row_index, values)
    source_rows = [
        ["데이터", "소상공인시장진흥공단 상가(상권)정보 API", "https://www.data.go.kr/data/15012005/openapi.do", "공공데이터포털 이용허락범위 제한 없음; 쿼터 준수", "주변 상가 조회"],
        ["문서/RAG", "카드사·통신사 공식 혜택 문서(후속)", "각 공식 상품 페이지", "저작권·수집 허용 범위 확인; 원문 재배포 금지", "혜택 근거 검색"],
        ["오픈소스", "Flutter·FastAPI·Google ADK 및 의존 패키지", "각 공식 GitHub/pub.dev/PyPI", "각 프로젝트 LICENSE 준수", "Frontend·Backend·Agent"],
        ["이미지/아이콘", "Flutter Material Icons·자체 작성 다이어그램", "https://fonts.google.com/icons", "Material Icons Apache 2.0; 다이어그램 자체 제작", "앱 UI·문서"],
        ["AI 모델/API", "Vertex AI Gemini 2.5 Flash·Google Maps", "https://cloud.google.com/vertex-ai / https://developers.google.com/maps", "Google Cloud/Maps 약관·과금·키 제한 준수", "Agent 설명·지도"],
    ]
    for row_index, values in enumerate(source_rows, start=1):
        set_row(tables, 80, row_index, values)
    set_cell(tables, 81, 0, 0, "README 재현 절차\n1. 저장소 clone 후 backend에서 Python 3.11 venv 생성, pip install -e \".[dev]\"\n2. .env.example을 참고해 프로젝트·저장소·모델 설정; 실제 Secret은 파일에 기록하지 않음\n3. uvicorn app.main:app --reload로 API 실행, /health·/docs 확인\n4. frontend에서 flutter pub get 후 API_BASE_URL·GOOGLE_MAPS_API_KEY를 dart-define으로 전달\n5. pytest·ruff, flutter analyze·flutter test 실행\n6. 공공 API 키를 Secret Manager에 저장하고 런타임 서비스 계정에 accessor 부여\n7. GitHub push로 Cloud Build→Cloud Run, flutter build web 후 firebase deploy\n8. 배포 URL, health, 주변 API, Secret 미노출, 최신 commit을 최종 확인")
    checklist_values = ["[✓]", "[✓]", "[✓]", "[✓]", "[✓]", "[미완]", "[✓]", "[✓]", "[미완]", "[부분]", "[미완]", "[✓]"]
    for row_index, value in enumerate(checklist_values, start=1):
        set_cell(tables, 83, row_index, 0, value)
    set_cell(tables, 84, 0, 0, "미확인/제출 비고\n- 공식 카드·통신사 RAG는 설계와 안전 응답만 구현되어 검색 평가 결과가 없다.\n- 정식 외부 사용자 테스트와 응답시간 반복 측정은 미실시다.\n- 발표자료·시연 영상·최신 배포 화면 캡처는 별도 준비가 필요하다.\n- 문서 작성 시 로컬 최신 commit은 ddd365f이며 GitHub push 후 Cloud Run/Firebase가 동일 commit인지 확인해야 한다.\n- 상가정보의 프랜차이즈 누락은 알려진 데이터 제약이며 Google Places/공식 매장 데이터로 보완한다.")
    set_row(tables, 85, 1, ["팀 대표", "김형우", "2026-08-11", "확인"])
    for row_index in (2, 3, 4):
        set_row(tables, 85, row_index, ["팀원", "해당 없음(개인 프로젝트)", "2026-08-11", "-"])

    image_descriptions = [
        "쿠폰콕 시스템 아키텍처: Flutter, Cloud Run, ADK, Gemini, Firestore, 공공데이터와 후속 RAG의 연결 구조",
        "쿠폰콕 에이전트 처리 흐름: GPS와 결제금액 입력부터 쿠폰 필터, 거리순 Top 5, 가격 계산, Gemini 설명까지의 순서",
    ]
    for image_index, doc_properties in enumerate(root.xpath(".//*[local-name()='docPr']")):
        if image_index < len(image_descriptions):
            doc_properties.set("descr", image_descriptions[image_index])
            doc_properties.set("title", image_descriptions[image_index])

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone="yes")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(SOURCE, "r") as source_package:
        parts = {info.filename: source_package.read(info.filename) for info in source_package.infolist()}
        infos = {info.filename: info for info in source_package.infolist()}

    parts["word/document.xml"] = fill(parts["word/document.xml"])
    parts["word/media/image1.png"] = (WORK / "generated" / "image1.png").read_bytes()
    parts["word/media/image2.png"] = (WORK / "generated" / "image2.png").read_bytes()

    with ZipFile(OUTPUT, "w", compression=ZIP_DEFLATED) as output_package:
        for filename, data in parts.items():
            original = infos[filename]
            info = ZipInfo(filename, date_time=original.date_time)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = original.external_attr
            info.internal_attr = original.internal_attr
            info.create_system = original.create_system
            output_package.writestr(info, data)

    print(OUTPUT)


if __name__ == "__main__":
    main()
