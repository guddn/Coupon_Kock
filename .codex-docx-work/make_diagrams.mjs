import sharp from 'file:///C:/Users/hello/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/lib/index.js';
import { mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const out = new URL('./generated/', import.meta.url);
await mkdir(out, { recursive: true });

const common = `
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">
      <path d="M0,0 L10,4 L0,8 Z" fill="#29435f"/>
    </marker>
    <style>
      .box { fill:#f7fbff; stroke:#5b8fc5; stroke-width:2; }
      .plan { fill:#faf8ff; stroke:#8267c7; stroke-width:2; stroke-dasharray:8 6; }
      .label { font-family:'Malgun Gothic','Noto Sans CJK KR',Arial,sans-serif; font-size:18px; fill:#182b3f; text-anchor:middle; }
      .small { font-family:'Malgun Gothic','Noto Sans CJK KR',Arial,sans-serif; font-size:14px; fill:#53677c; text-anchor:middle; }
      .line { fill:none; stroke:#29435f; stroke-width:2; marker-end:url(#arrow); }
    </style>
  </defs>`;

const architecture = `
<svg xmlns="http://www.w3.org/2000/svg" width="1198" height="220" viewBox="0 0 1198 220">
${common}
<rect width="1198" height="220" fill="white"/>
<rect class="box" x="15" y="25" rx="14" width="185" height="70"/>
<text class="label" x="108" y="55">Flutter Web / App</text><text class="small" x="108" y="78">Firebase Hosting · GPS · Maps</text>
<rect class="box" x="265" y="25" rx="14" width="190" height="70"/>
<text class="label" x="360" y="55">FastAPI · Cloud Run</text><text class="small" x="360" y="78">Validation · API orchestration</text>
<rect class="box" x="520" y="25" rx="14" width="175" height="70"/>
<text class="label" x="608" y="55">Google ADK Agent</text><text class="small" x="608" y="78">Tool calls · trace</text>
<rect class="box" x="760" y="25" rx="14" width="175" height="70"/>
<text class="label" x="848" y="55">Vertex AI Gemini</text><text class="small" x="848" y="78">Evidence explanation</text>
<path class="line" d="M200 60 H265"/><path class="line" d="M455 60 H520"/><path class="line" d="M695 60 H760"/>

<rect class="box" x="15" y="135" rx="14" width="185" height="65"/>
<text class="label" x="108" y="163">Secret Manager</text><text class="small" x="108" y="184">Public API key</text>
<rect class="box" x="265" y="135" rx="14" width="190" height="65"/>
<text class="label" x="360" y="163">Public Store OpenAPI</text><text class="small" x="360" y="184">Nearby candidates · coordinates</text>
<rect class="box" x="520" y="135" rx="14" width="175" height="65"/>
<text class="label" x="608" y="163">Cloud Firestore</text><text class="small" x="608" y="184">Registered coupons</text>
<rect class="plan" x="760" y="135" rx="14" width="235" height="65"/>
<text class="label" x="878" y="163">Benefit RAG · Planned</text><text class="small" x="878" y="184">Official card / telecom docs</text>
<path class="line" d="M360 95 V135"/><path class="line" d="M608 95 V135"/>
<path class="line" d="M108 135 V112 H315 V95"/><path class="line" d="M878 135 V112 H650 V95"/>
</svg>`;

const pipeline = `
<svg xmlns="http://www.w3.org/2000/svg" width="1418" height="442" viewBox="0 0 1418 442">
${common}
<rect width="1418" height="442" fill="white"/>
<rect class="box" x="25" y="45" rx="10" width="235" height="85"/><text class="label" x="143" y="82">GPS · 결제금액</text><text class="small" x="143" y="107">Flutter foreground location</text>
<rect class="box" x="365" y="45" rx="10" width="250" height="85"/><text class="label" x="490" y="82">주변 매장 조회</text><text class="small" x="490" y="107">Public data · radius 1 km</text>
<rect class="box" x="720" y="45" rx="10" width="250" height="85"/><text class="label" x="845" y="82">유효 쿠폰 조회</text><text class="small" x="845" y="107">Firestore · expiry filter</text>
<rect class="box" x="1075" y="45" rx="10" width="280" height="85"/><text class="label" x="1215" y="82">브랜드 사용 가능 매장</text><text class="small" x="1215" y="107">Coupon ↔ store name match</text>
<path class="line" d="M260 88 H365"/><path class="line" d="M615 88 H720"/><path class="line" d="M970 88 H1075"/>

<rect class="box" x="165" y="285" rx="10" width="260" height="85"/><text class="label" x="295" y="322">거리 재계산 · Top 5</text><text class="small" x="295" y="347">Haversine · ascending order</text>
<rect class="box" x="565" y="285" rx="10" width="250" height="85"/><text class="label" x="690" y="322">가격 계산 Tool</text><text class="small" x="690" y="347">Deterministic options</text>
<rect class="box" x="955" y="285" rx="10" width="275" height="85"/><text class="label" x="1093" y="322">Gemini 근거 설명</text><text class="small" x="1093" y="347">Result unchanged · tool trace</text>
<path class="line" d="M1215 130 V220 H295 V285"/><path class="line" d="M425 328 H565"/><path class="line" d="M815 328 H955"/>
<rect class="plan" x="1245" y="265" rx="10" width="150" height="125"/><text class="label" x="1320" y="310">RAG</text><text class="small" x="1320" y="335">공식 카드·통신사</text><text class="small" x="1320" y="358">후속 연동</text><path class="line" d="M1245 328 H1230"/>
</svg>`;

await sharp(Buffer.from(architecture)).png().toFile(fileURLToPath(new URL('image1.png', out)));
await sharp(Buffer.from(pipeline)).png().toFile(fileURLToPath(new URL('image2.png', out)));
console.log('generated diagrams');
