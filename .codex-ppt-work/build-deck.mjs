import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";
import { buildSlide02 } from "./layouts/slide-02.mjs";
import { buildSlide04 } from "./layouts/slide-04.mjs";
import { buildSlide08 } from "./layouts/slide-08.mjs";
import { buildSlide13 } from "./layouts/slide-13.mjs";
import { buildSlide17 } from "./layouts/slide-17.mjs";
import { buildSlide19 } from "./layouts/slide-19.mjs";
import { buildSlide26 } from "./layouts/slide-26.mjs";

const ROOT = "D:/development/Github/_AJOU_class/2026-1_AI_Bootcamp/Coupon_Kock";
const WORK = `${ROOT}/.codex-ppt-work`;
const OUT = `${ROOT}/deliverables/쿠폰콕_포트폴리오_15p.pptx`;
const RENDER = `${WORK}/rendered`;
const FONT = "Noto Sans KR";
const INK = "#111111";
const MUTED = "#5F6368";
const ACCENT = "#F7C948";

function textBlock(text, size = 24, bold = false, color = INK, options = {}) {
  return {
    runs: [{
      run: text,
      textStyle: {
        fontSize: `${size}px`,
        typeface: FONT,
        color,
        bold,
      },
    }],
    spaceBefore: options.spaceBefore ?? 0,
    spaceAfter: options.spaceAfter ?? 650,
    paragraphStyle: {
      lineSpacingPercent: options.lineSpacingPercent ?? 112000,
      alignment: options.alignment ?? "left",
    },
  };
}

const blank = () => textBlock("", 20, false, MUTED, { spaceAfter: 0 });
const slideTitle = (text) => textBlock(text, 46, true, INK, { lineSpacingPercent: 94000 });
const sectionTitle = (text) => textBlock(text, 25, true, INK, { spaceAfter: 550 });
const body = (text) => textBlock(text, 21, false, MUTED, { spaceAfter: 750, lineSpacingPercent: 122000 });
const bodyStrong = (text) => textBlock(text, 22, true, INK, { spaceAfter: 650 });
const label = (text) => textBlock(text, 18, true, MUTED, { spaceAfter: 0 });
const stat = (text) => textBlock(text, 52, true, INK, { spaceAfter: 0 });
const footer = (n) => textBlock(String(n).padStart(2, "0"), 14, false, MUTED, { spaceAfter: 0, alignment: "right" });

function titleOnly(text, n) {
  return {
    title: slideTitle(text),
    body1: {
      titleHere: blank(),
      loremIpsumDolorSitAmetConsecteturAdipiscing: blank(),
      loremIpsumDolorSitAmetConsecteturAdipiscing2: blank(),
      loremIpsumDolorSitAmetConsecteturAdipiscing3: blank(),
    },
    body2: {
      loremIpsumDolorSitAmetConsecteturAdipiscing: blank(),
      loremIpsumDolorSitAmetConsecteturAdipiscing2: blank(),
      loremIpsumDolorSitAmetConsecteturAdipiscing3: blank(),
    },
    footer1: footer(n),
  };
}

function addAccent(slide) {
  slide.shapes.add({
    geometry: "rect",
    name: "coupon-kock-accent",
    position: { left: 41, top: 121, width: 112, height: 7 },
    fill: ACCENT,
    line: { style: "solid", fill: ACCENT, width: 0 },
  });
}

function addNotes(slide, sources, presenter = "") {
  const lines = [];
  if (presenter) lines.push(presenter, "");
  lines.push("[Sources]", ...sources.map((source) => `- ${source}`));
  slide.speakerNotes.textFrame.setText(lines.join("\n"));
}

async function imageBuffer(filePath) {
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

async function addImage(slide, filePath, alt, position, fit = "contain") {
  slide.images.add({
    blob: await imageBuffer(filePath),
    contentType: "image/png",
    alt,
    fit,
    position,
  });
}

function twoColumnTokens(title, left, right, n) {
  const leftLines = left.lines ?? [];
  const rightLines = right.lines ?? [];
  return {
    title: slideTitle(title),
    body1: {
      titleHere: sectionTitle(left.title),
      loremIpsumDolorSitAmetConsecteturAdipiscing: body(leftLines[0] ?? ""),
      loremIpsumDolorSitAmetConsecteturAdipiscing2: body(leftLines[1] ?? ""),
      loremIpsumDolorSitAmetConsecteturAdipiscing3: body(leftLines[2] ?? ""),
    },
    body2: {
      loremIpsumDolorSitAmetConsecteturAdipiscing: sectionTitle(right.title),
      loremIpsumDolorSitAmetConsecteturAdipiscing2: body(rightLines[0] ?? ""),
      loremIpsumDolorSitAmetConsecteturAdipiscing3: body(rightLines[1] ?? ""),
    },
    footer1: footer(n),
  };
}

function fourPointTokens(title, points, n) {
  const mapped = points.map((point) => ({
    titleGoesHere: sectionTitle(point.title),
    loremIpsumDolorSitAmetConsecteturAdipiscing: body(point.body),
  }));
  return {
    title: slideTitle(title),
    body1: mapped[0],
    body2: mapped[1],
    body3: mapped[2],
    body4: mapped[3],
    footer1: footer(n),
  };
}

function timelineTokens(title, milestones, n) {
  return {
    title: slideTitle(title),
    label1: label(milestones[0].label),
    label2: label(milestones[1].label),
    label3: label(milestones[2].label),
    body1: { titleHere: sectionTitle(milestones[0].title), loremIpsumDolorSitAmetConsecteturAdipiscing: body(milestones[0].body) },
    body2: { titleHere: sectionTitle(milestones[1].title), loremIpsumDolorSitAmetConsecteturAdipiscing: body(milestones[1].body) },
    body3: { titleHere: sectionTitle(milestones[2].title), loremIpsumDolorSitAmetConsecteturAdipiscing: body(milestones[2].body) },
    footer1: footer(n),
  };
}

function metricTokens(title, lead, metrics, n) {
  return {
    title: slideTitle(title),
    body1: { topic: bodyStrong(lead), loremIpsumDolorSitAmetConsecteturAdipiscing: blank() },
    stat1: stat(metrics[0].value),
    stat2: stat(metrics[1].value),
    stat3: stat(metrics[2].value),
    body2: body(metrics[0].label),
    body3: body(metrics[1].label),
    body4: body(metrics[2].label),
    footer1: footer(n),
  };
}

async function addDiagramSlide(presentation, title, imagePath, alt, n, caption, sources) {
  const slide = buildSlide04(presentation, titleOnly(title, n));
  slide.shapes.add({
    geometry: "rect",
    name: "diagram-clean-field",
    position: { left: 41, top: 148, width: 1198, height: 493 },
    fill: "#FFFFFF",
    line: { style: "solid", fill: "#FFFFFF", width: 0 },
  });
  await addImage(slide, imagePath, alt, { left: 62, top: 166, width: 1156, height: 420 }, "contain");
  const captionShape = slide.shapes.add({
    geometry: "textbox",
    name: "diagram-caption",
    position: { left: 62, top: 596, width: 1050, height: 38 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  captionShape.text = caption;
  captionShape.text.style = { fontSize: 18, typeface: FONT, color: MUTED };
  addAccent(slide);
  addNotes(slide, sources);
  return slide;
}

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function main() {
  await fs.mkdir(RENDER, { recursive: true });
  await fs.mkdir(path.dirname(OUT), { recursive: true });

  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

  // 1 — cover
  let slide = buildSlide02(presentation, {
    title: textBlock("PORTFOLIO · 2026", 22, true, MUTED),
    title2: textBlock("KIM HYEONGWOO", 22, true, MUTED),
    title3: textBlock("쿠폰콕\n위치 기반 쿠폰 혜택 에이전트", 74, true, INK, { lineSpacingPercent: 92000 }),
  });
  slide.shapes.add({ geometry: "rect", position: { left: 41, top: 236, width: 132, height: 10 }, fill: ACCENT, line: { style: "solid", fill: ACCENT, width: 0 } });
  addNotes(slide, [`${ROOT}/deliverables/AJOU_PBL_1차_MVP_쿠폰콕_통합제출서.docx`], "개인 프로젝트 · Flutter / GCP / ADK");

  // 2 — problem
  slide = buildSlide08(presentation, {
    title: slideTitle("결제 직전, 혜택은 흩어져 있다"),
    body1: {
      titleHere: sectionTitle("사용자의 실제 문제"),
      loremIpsumDolorSitAmetConsecteturAdipiscing: body("쿠폰은 이미지·앱·문자에 흩어져 있고, 매장·유효기간·결제금액과 연결되지 않는다.\n\n결국 사용자는 혜택을 보유하고도 적용 시점을 놓친다."),
    },
    footer1: footer(2),
  });
  await addImage(slide, `${WORK}/assets/gifticon.png`, "바코드가 마스킹된 모바일 쿠폰 예시", { left: 774, top: 77, width: 350, height: 515 }, "contain");
  addAccent(slide);
  addNotes(slide, [`${ROOT}/coupons_img/gifticon.png`, `${ROOT}/deliverables/AJOU_PBL_1차_MVP_쿠폰콕_통합제출서.docx`]);

  // 3 — solution
  slide = buildSlide17(presentation, timelineTokens("등록부터 추천까지 하나의 사용자 흐름으로 묶었다", [
    { label: "STEP 01", title: "쿠폰 등록", body: "브랜드·상품·금액·유효기간을 저장하고 사용자별로 관리" },
    { label: "STEP 02", title: "주변 탐색", body: "GPS와 공공 상가데이터를 결합해 사용 가능한 매장만 선별" },
    { label: "STEP 03", title: "혜택 추천", body: "결정적 계산 결과를 ADK와 Gemini가 근거 중심으로 설명" },
  ], 3));
  addAccent(slide);
  addNotes(slide, [`${ROOT}/docs/architecture.md`, `${ROOT}/frontend/lib/features/coupons/coupon_screen.dart`, `${ROOT}/frontend/lib/features/nearby/nearby_screen.dart`]);

  // 4 — core product
  slide = buildSlide13(presentation, fourPointTokens("핵심 기능은 사용자 가치와 직접 연결된다", [
    { title: "쿠폰 등록·관리", body: "Firestore 영속화와 사용자별 조회로 재사용 가능한 데이터화" },
    { title: "위치 기반 Top 5", body: "현재 위치에서 실제 거리를 다시 계산해 가까운 순으로 정렬" },
    { title: "쿠폰–매장 필터", body: "보유 쿠폰 브랜드와 일치하는 매장만 지도와 목록에 표시" },
    { title: "혜택 계산·설명", body: "Python calculator가 금액을 결정하고 Gemini는 근거만 설명" },
  ], 4));
  addAccent(slide);
  addNotes(slide, [`${ROOT}/backend/app/services/coupon_registry.py`, `${ROOT}/backend/app/services/recommendation.py`, `${ROOT}/frontend/lib/features/nearby/nearby_screen.dart`]);

  // 5 — UI QA
  slide = buildSlide08(presentation, {
    title: slideTitle("지도 QA로 거리·정렬을 고쳤다"),
    body1: {
      titleHere: sectionTitle("발견 → 수정"),
      loremIpsumDolorSitAmetConsecteturAdipiscing: body("초기 화면에서 지도 잘림과 91m 중복 표시를 확인했다.\n\n탭 활성 시 지도 생성, 전체 영역 배치, 최신 GPS 기준 Haversine 재계산, 오름차순 정렬을 적용했다."),
    },
    footer1: footer(5),
  });
  await addImage(slide, `${WORK}/assets/map-qa-before.png`, "지도 잘림과 동일 거리 표시를 보여주는 초기 QA 화면", { left: 768, top: 58, width: 388, height: 570 }, "contain");
  addAccent(slide);
  addNotes(slide, [`${WORK}/assets/map-qa-before.png`, `${ROOT}/frontend/lib/features/nearby/nearby_screen.dart`, `${ROOT}/deliverables/AJOU_PBL_1차_MVP_쿠폰콕_통합제출서.docx`]);

  // 6 — architecture
  await addDiagramSlide(presentation, "Flutter부터 Gemini까지 하나의 GCP 경계로 연결했다", `${WORK}/assets/system-architecture.png`, "쿠폰콕 시스템 아키텍처", 6, "Frontend · API · Agent · Data · Infra의 책임을 분리하고 Secret은 런타임 계정에만 주입", [`${ROOT}/docs/architecture.md`, `${ROOT}/deliverables/AJOU_PBL_1차_MVP_쿠폰콕_통합제출서.docx`]);

  // 7 — agent pipeline
  await addDiagramSlide(presentation, "에이전트는 매장 후보를 줄인 뒤 가격을 계산한다", `${WORK}/assets/agent-pipeline.png`, "쿠폰콕 에이전트 처리 파이프라인", 7, "GPS → 공공데이터 → 유효 쿠폰 → 브랜드 매칭 → 거리 Top 5 → 가격 계산 → Gemini 근거 설명", [`${ROOT}/backend/app/agents/coupon_kock_agent/agent.py`, `${ROOT}/backend/app/agents/coupon_kock_agent/tools.py`, `${ROOT}/docs/architecture.md`]);

  // 8 — ADK
  slide = buildSlide13(presentation, fourPointTokens("ADK는 판단 과정과 계산 책임을 분리한다", [
    { title: "store_match", body: "위치와 매장 후보를 검증해 잘못된 매장 진입을 차단" },
    { title: "benefit context", body: "사용자 쿠폰과 후속 공식 혜택 RAG의 근거 상태를 로드" },
    { title: "rule validator", body: "유효기간·브랜드·조건을 검사하고 근거 없는 규칙은 제외" },
    { title: "price calculator", body: "LLM 밖의 결정적 코드가 최종 금액과 절감액을 산출" },
  ], 8));
  addAccent(slide);
  addNotes(slide, [`${ROOT}/backend/app/agents/coupon_kock_agent/agent.py`, `${ROOT}/backend/app/agents/coupon_kock_agent/tools.py`, `${ROOT}/backend/tests/test_adk_agent.py`]);

  // 9 — public data
  slide = buildSlide04(presentation, twoColumnTokens("공공데이터는 후보를 만들고, 쿠폰 데이터가 의미를 만든다", {
    title: "공공 상가데이터의 역할",
    lines: ["• 반경 내 매장 후보와 좌표 조회", "• Cloud Run에서 인증키를 Secret으로 호출", "• 실패 시 fixture와 notice로 출처를 구분"],
  }, {
    title: "서비스 계층의 보정",
    lines: ["쿠폰 브랜드 매칭 → Haversine 재계산 → 오름차순 정렬 → Top 5", "브랜드 누락은 Google Places·공식 Store Master로 보완 예정"],
  }, 9));
  addAccent(slide);
  addNotes(slide, [`${ROOT}/docs/public-data.md`, "https://www.data.go.kr/data/15012005/openapi.do", `${ROOT}/backend/tests/test_coupons_and_stores.py`]);

  // 10 — API
  slide = buildSlide13(presentation, fourPointTokens("프론트와 백엔드는 명확한 API 계약으로 연결된다", [
    { title: "POST /api/coupons", body: "브랜드·상품·금액·유효기간을 검증하고 Firestore에 저장" },
    { title: "GET /api/stores/nearby", body: "사용자·좌표·반경·limit으로 쿠폰 사용 가능 Top 5 반환" },
    { title: "POST /api/recommendations", body: "결제금액과 후보를 받아 예상 최종 금액을 계산" },
    { title: "POST /api/agent/recommendations", body: "ADK 실행 결과와 answer·tool_trace를 함께 반환" },
  ], 10));
  addAccent(slide);
  addNotes(slide, [`${ROOT}/docs/api.md`, "https://coupon-kock-663890381698.asia-northeast3.run.app/docs"]);

  // 11 — deployment
  slide = buildSlide17(presentation, timelineTokens("Git push가 웹과 API 배포로 이어지도록 자동화했다", [
    { label: "SOURCE", title: "GitHub main", body: "기능 단위 커밋과 문서로 변경 범위를 추적" },
    { label: "BACKEND", title: "Cloud Build → Run", body: "Docker 이미지 생성, Artifact Registry, 새 Revision 배포" },
    { label: "FRONTEND", title: "Flutter → Firebase", body: "dart-define으로 환경을 주입해 Web release를 Hosting에 배포" },
  ], 11));
  addAccent(slide);
  addNotes(slide, [`${ROOT}/README.md`, `${ROOT}/docs/implementation-plan.md`, "https://github.com/guddn/Coupon_Kock"]);

  // 12 — troubleshooting
  slide = buildSlide04(presentation, twoColumnTokens("배포 문제는 계정·런타임·데이터 경계를 분리해 해결했다", {
    title: "막혔던 지점",
    lines: ["• Developer Connect 읽기 토큰 403", "• Backend 경로 대소문자·Docker context 오류", "• Secret Manager 접근 거부와 공공 API 키 오류"],
  }, {
    title: "해결 원칙",
    lines: ["빌드 계정과 Cloud Run 런타임 계정의 IAM을 분리하고 최소 역할을 부여", "실패 원인을 UI 메시지와 data_source·notice로 노출해 디버깅 가능성 확보"],
  }, 12));
  addAccent(slide);
  addNotes(slide, [`${ROOT}/deliverables/AJOU_PBL_1차_MVP_쿠폰콕_통합제출서.docx`, `${ROOT}/README.md`]);

  // 13 — validation
  slide = buildSlide19(presentation, metricTokens("자동화 테스트와 배포 상태로 MVP의 핵심 가설을 검증했다", "계산과 필터는 결정적 코드로 검증하고, 생성 모델은 결과를 바꾸지 않도록 제한했다.", [
    { value: "21", label: "Backend 16 + Flutter 5\n자동화 테스트 통과" },
    { value: "200", label: "Cloud Run /health\n정상 응답" },
    { value: "Top 5", label: "쿠폰 브랜드 필터 후\n거리순 추천" },
  ], 13));
  addAccent(slide);
  addNotes(slide, [`${ROOT}/backend/tests`, `${ROOT}/frontend/test`, `${ROOT}/deliverables/AJOU_PBL_1차_MVP_쿠폰콕_통합제출서.docx`]);

  // 14 — scope and roadmap
  slide = buildSlide04(presentation, twoColumnTokens("완성한 MVP와 다음 확장 범위를 의도적으로 구분했다", {
    title: "현재 시연 가능",
    lines: ["쿠폰 수동 등록·Firestore 조회", "GPS·지도·공공데이터·쿠폰 매장 Top 5", "결정적 혜택 계산·ADK tool_trace·Cloud 배포"],
  }, {
    title: "다음 우선순위",
    lines: ["Google Places·공식 Store Master로 브랜드 coverage 보완", "Firebase Auth → Android OCR → 공식 카드·통신사 Vector RAG → geofencing 알림"],
  }, 14));
  addAccent(slide);
  addNotes(slide, [`${ROOT}/docs/implementation-plan.md`, `${ROOT}/deliverables/AJOU_PBL_1차_MVP_쿠폰콕_통합제출서.docx`]);

  // 15 — close
  slide = buildSlide26(presentation, {
    title: textBlock("FULL-STACK AI PROJECT", 22, true, MUTED),
    title2: textBlock("쿠폰콕은\n‘작동하는 연결’을 증명했다", 68, true, INK, { lineSpacingPercent: 92000 }),
    title3: {
      loremIpsumDetails: bodyStrong("Flutter Web · FastAPI · Cloud Run · Firestore"),
      loremIpsumDetails2: body("github.com/guddn/Coupon_Kock"),
      loremIpsumDetails3: body("proj-aj25-211200020328.web.app"),
    },
  });
  slide.shapes.add({ geometry: "rect", position: { left: 41, top: 468, width: 132, height: 10 }, fill: ACCENT, line: { style: "solid", fill: ACCENT, width: 0 } });
  addNotes(slide, ["https://github.com/guddn/Coupon_Kock", "https://proj-aj25-211200020328.web.app", "https://coupon-kock-663890381698.asia-northeast3.run.app/docs"]);

  for (const [index, currentSlide] of presentation.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(`${RENDER}/${stem}.png`, await presentation.export({ slide: currentSlide, format: "png", scale: 1 }));
    const layout = await currentSlide.export({ format: "layout" });
    await fs.writeFile(`${RENDER}/${stem}.layout.json`, await layout.text());
  }

  await writeBlob(`${RENDER}/montage.webp`, await presentation.export({ format: "webp", montage: true, scale: 1 }));
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(OUT);
  console.log(JSON.stringify({ output: OUT, slides: presentation.slides.items.length }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
