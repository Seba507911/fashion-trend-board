/**
 * WGSN 26SS Expert Report — Structured Data
 * Source: WGSN 77 reports (NotebookLM analysis)
 * Used by: ExpertReview.jsx (blog-style report review page)
 */

// ─── Section Navigation ─────────────────────────────────────
export const SECTIONS = [
  { id: "overview", title: "분석 개요", subtitle: "WGSN 77건 → NotebookLM → 101 키워드" },
  { id: "color", title: "컬러 시그널", subtitle: "28개 키워드 · Tier 1~3" },
  { id: "material", title: "소재 시그널", subtitle: "20개 키워드 · Tier 1~3" },
  { id: "silhouette", title: "실루엣 시그널", subtitle: "18개 키워드 · Tier 1~4" },
  { id: "item", title: "아이템 시그널", subtitle: "21개 키워드 · Tier 1~3" },
  { id: "style", title: "스타일 / 매크로 테마", subtitle: "7개 합의 + 5개 니치 예측" },
  { id: "data", title: "데이터 기반 시그널", subtitle: "소셜 버즈 · YoY · 컬렉션 점유율" },
  { id: "brand", title: "F&F 브랜드 관련성", subtitle: "브랜드-트렌드 매핑" },
  { id: "pool", title: "풀 A/B 초안 검증", subtitle: "런웨이 교차검증 전 분류" },
  { id: "method", title: "방법론 & 다음 단계", subtitle: "분석 보완 방향 논의" },
];

// ─── Color ───────────────────────────────────────────────────
export const COLOR_SIGNAL_SUMMARY = [
  "지배 트렌드: 미드톤/뉴트럴(브라운, 베이지, 그레이) 베이스 + Statement Red 포인트",
  "신규 시그널: Transformative Teal (2026 올해의 컬러 COTY), Gelato Pastels (Blue Aura 중심)",
  "FTIB 매핑 키워드: navy, black, white, beige, teal, red/cherry/crimson, sage, mint, pink, yellow, brown/chocolate, purple/grape",
];

export const COLOR_KEYWORDS = {
  tier1: {
    label: "Tier 1 — 핵심 합의 (10개+ 소스)",
    items: [
      { keyword: "Blue Aura", kr: "블루 오라", sources: 13, theme: "Gelato Pastels", pool: "A", note: "파스텔 포인트 컬러" },
      { keyword: "Celestial Yellow", kr: "셀레스티얼 옐로우", sources: 12, theme: "Joyous Brights", pool: "A", note: "밝은 옐로우, 에너지와 낙관" },
      { keyword: "Dusted Grape", kr: "더스티드 그레이프", sources: 12, theme: "Berry Tones", pool: "A", note: "보라/포도 톤, 성숙한 깊이" },
      { keyword: "Optic White", kr: "옵틱 화이트", sources: 10, theme: "Minimalist Base", pool: "A", note: "깨끗한 화이트 베이스" },
      { keyword: "Classic Navy", kr: "클래식 네이비", sources: 10, theme: "Nautical / Base", pool: "A", note: "시즌 내내 안정적 수요" },
      { keyword: "Black", kr: "블랙", sources: 10, theme: "Base", pool: null, note: "시즌 불문 베이스" },
      { keyword: "Transformative Teal", kr: "트랜스포머티브 틸", sources: 10, theme: "2026 COTY", pool: "B", note: "WGSN+Coloro 올해의 컬러, 자연과 기술의 균형" },
    ],
  },
  tier2: {
    label: "Tier 2 — 주요 (8~9개 소스)",
    items: [
      { keyword: "Pink Frost", kr: "핑크 프로스트", sources: 9, theme: "Pretty Feminine", pool: "A" },
      { keyword: "Amber Haze", kr: "앰버 헤이즈", sources: 9, theme: "Warm Neutrals", pool: null },
      { keyword: "Sage Green", kr: "세이지 그린", sources: 9, theme: "Nature / Outdoor", pool: "A" },
      { keyword: "Chalk", kr: "초크", sources: 9, theme: "Neutral Base", pool: null },
      { keyword: "Cherry Lacquer", kr: "체리 라커", sources: 8, theme: "Statement Reds", pool: "A" },
      { keyword: "Peach Jelly", kr: "피치 젤리", sources: 8, theme: "Gelato Pastels", pool: "A" },
      { keyword: "Jelly Mint", kr: "젤리 민트", sources: 8, theme: "Gelato Pastels", pool: "A" },
      { keyword: "Midnight Blue", kr: "미드나잇 블루", sources: 8, theme: "Dark Tones", pool: null },
      { keyword: "Lava Red", kr: "라바 레드", sources: 8, theme: "Statement Reds", pool: "A" },
      { keyword: "Chocolate Sauce", kr: "초콜릿 소스", sources: 8, theme: "Dark Browns", pool: null },
      { keyword: "Vivid Yellow", kr: "비비드 옐로우", sources: 8, theme: "Joyous Brights", pool: "A" },
      { keyword: "Robust Red", kr: "로버스트 레드", sources: 8, theme: "Statement Reds", pool: "A" },
      { keyword: "Future Grey", kr: "퓨처 그레이", sources: 8, theme: "Neutral Base", pool: null },
      { keyword: "Crimson", kr: "크림슨", sources: 8, theme: "Statement Reds", pool: "A" },
      { keyword: "Classic Beige", kr: "클래식 베이지", sources: 8, theme: "Neutral Base", pool: null },
    ],
  },
  tier3: {
    label: "Tier 3 — 서브 (6~7개 소스)",
    items: [
      { keyword: "Electric Fuchsia", kr: "일렉트릭 퓨샤", sources: 7, theme: "Joyous Brights", pool: "A" },
      { keyword: "Thrift Pink", kr: "스리프트 핑크", sources: 7, theme: "Pretty Feminine", pool: null },
      { keyword: "Sea Kelp", kr: "씨 켈프", sources: 7, theme: "Nature Tones", pool: null },
      { keyword: "Circular Grey", kr: "서큘러 그레이", sources: 7, theme: "Neutral", pool: null },
      { keyword: "Blue Gleam", kr: "블루 글림", sources: 7, theme: "Gelato Pastels", pool: "A" },
      { keyword: "Retro Green", kr: "레트로 그린", sources: 7, theme: "Retro / 80s", pool: null },
    ],
  },
};

// ─── Material ────────────────────────────────────────────────
export const MATERIAL_SIGNAL_SUMMARY = [
  "지배 트렌드: Sheer(투명) + Lace(레이스) = 관능미/여성성의 양대 소재",
  "기본 바탕: 친환경 천연섬유 (Cotton, Linen, Hemp, Tencel)",
  "질감 트렌드: 은은한 3D 텍스처 (크링클, 해머드, 자카드)",
  "FTIB 매핑 키워드: sheer, lace, knit, cotton, leather, denim, linen, silk, satin, suede, wool",
];

export const MATERIAL_KEYWORDS = {
  tier1: {
    label: "Tier 1 — 핵심 합의 (7개+ 소스)",
    items: [
      { keyword: "Sheer", kr: "시어/투명", sources: 11, usage: "시폰, 오간자 — 레이어링, Day-to-Night", pool: "A", note: "이번 시즌 가장 지배적인 패브릭" },
      { keyword: "Lace", kr: "레이스", sources: 11, usage: "Pretty Feminine, Dark Romance", pool: "A", note: "관능미와 여성성" },
      { keyword: "Knit / Jersey", kr: "니트/저지", sources: 10, usage: "라운지웨어, Cut & Sew 기본", pool: "A", note: "F&F 관련성 높음" },
      { keyword: "Cotton", kr: "코튼", sources: 7, usage: "친환경 인증(BCI, GOTS), 장수명", pool: null, note: "F&F 관련성 높음" },
      { keyword: "Leather", kr: "레더", sources: 7, usage: "광택/질감 — 아우터, 하의", pool: "A", note: "럭셔리 시그널" },
    ],
  },
  tier2: {
    label: "Tier 2 — 주요 (4~6개 소스)",
    items: [
      { keyword: "Denim", kr: "데님", sources: 6, usage: "Y2K, 오피스코어, 리워크드", pool: "A", note: "F&F 관련성 높음" },
      { keyword: "Linen", kr: "리넨", sources: 5, usage: "리조트, 여름 테일러링", pool: null },
      { keyword: "Hemp", kr: "헴프", sources: 5, usage: "친환경 혼방, 내구성", pool: "B" },
      { keyword: "Jacquard", kr: "자카드", sources: 5, usage: "톤온톤, 은은한 장식", pool: null },
      { keyword: "Twill", kr: "트윌", sources: 5, usage: "워크웨어, 오피스웨어", pool: null },
      { keyword: "Satin", kr: "새틴", sources: 4, usage: "무광/은은한 광택, Low Key Luxury", pool: null },
      { keyword: "Lyocell / Tencel", kr: "텐셀", sources: 4, usage: "친환경, 드레이프", pool: "B" },
      { keyword: "Crochet", kr: "크로셰", sources: 4, usage: "보헤미안, 비치 커버업", pool: null },
    ],
  },
  tier3: {
    label: "Tier 3 — 서브 (2~3개 소스)",
    items: [
      { keyword: "Poplin", kr: "포플린", sources: 3, usage: "클래식 셔츠", pool: null },
      { keyword: "Suede", kr: "스웨이드", sources: 3, usage: "Low Key Luxury", pool: null },
      { keyword: "Viscose", kr: "비스코스", sources: 3, usage: "FSC 인증 권장", pool: null },
      { keyword: "Merino Wool", kr: "메리노 울", sources: 3, usage: "사계절, 스포티", pool: null },
      { keyword: "Silk", kr: "실크", sources: 2, usage: "두피온, 질감 강조", pool: null },
      { keyword: "Ripstop", kr: "립스탑", sources: 2, usage: "기능성, 워크웨어", pool: null },
      { keyword: "Canvas", kr: "캔버스", sources: 2, usage: "작업복 테마", pool: null },
    ],
  },
};

// ─── Silhouette ──────────────────────────────────────────────
export const SILHOUETTE_SIGNAL_SUMMARY = [
  "양대 산맥: 상의 = 파워 숄더 + 허리 강조 / 하의 = 와이드~배럴 레그",
  "신규 주목: Barrel Leg (와이드 넘어 곡선형), Skinny 재부상 (2010 Revival)",
  "FTIB 매핑 키워드: oversized, wide, slim/skinny, crop, boxy, structured(shoulder)",
];

export const SILHOUETTE_KEYWORDS = {
  tier1: {
    label: "Tier 1 — 메가 트렌드 (15개+ 소스)",
    items: [
      { keyword: "Oversized / Relaxed", kr: "오버사이즈/릴랙스드", sources: "30+", note: "가장 지배적 — 전 복종", pool: "A" },
      { keyword: "Wide Leg", kr: "와이드 레그", sources: 22, note: "하의 1순위 실루엣", pool: "A" },
      { keyword: "Straight Leg", kr: "스트레이트 레그", sources: 20, note: "와이드 대안, 가장 빠른 성장", pool: "A" },
    ],
  },
  tier2: {
    label: "Tier 2 — 주요 트렌드 (10~15개 소스)",
    items: [
      { keyword: "Cropped", kr: "크롭", sources: 15, note: "상의/아우터 기장", pool: "A" },
      { keyword: "Sculpted Shoulder", kr: "파워 숄더/스컬프티드", sources: 14, note: "80년대 핵심 — +225% YoY", pool: "A" },
      { keyword: "Barrel Leg / Balloon", kr: "배럴/벌룬", sources: 12, note: "신규 부상 — 곡선 하의", pool: "A" },
      { keyword: "Skinny / Slim", kr: "스키니/슬림", sources: 11, note: "2010 Revival — 재테스트 중", pool: "A" },
    ],
  },
  tier3: {
    label: "Tier 3 — 서브 (6~9개 소스)",
    items: [
      { keyword: "High Rise", kr: "하이라이즈", sources: 8, note: "하의 웨이스트", pool: null },
      { keyword: "Slouchy", kr: "슬라우치", sources: 8, note: "파자마 드레싱 연관", pool: null },
      { keyword: "Short Short / Mini", kr: "숏숏/미니", sources: 7, note: "스포티/페스티벌", pool: null },
      { keyword: "Boxy", kr: "박시", sources: 7, note: "재킷, 티셔츠", pool: null },
      { keyword: "Waist Focus", kr: "허리 강조", sources: 7, note: "80년대 + 테일러링", pool: null },
      { keyword: "A-Line", kr: "에이라인", sources: 7, note: "스커트, 반바지", pool: null },
      { keyword: "Capri / 7부", kr: "카프리", sources: 6, note: "2010 Revival", pool: null },
      { keyword: "Low Rise", kr: "로우 라이즈", sources: 6, note: "2010 Revival", pool: null },
    ],
  },
  tier4: {
    label: "Tier 4 — 니치 (3~5개 소스)",
    items: [
      { keyword: "Drop Shoulder", kr: "드롭 숄더", sources: 5, note: "릴랙스 상의", pool: null },
      { keyword: "Column / Pencil", kr: "컬럼/펜슬", sources: 4, note: "스커트 핏", pool: null },
      { keyword: "Flared / Bootcut", kr: "플레어/부트컷", sources: 3, note: "레트로 하의", pool: null },
    ],
  },
};

// ─── Item ────────────────────────────────────────────────────
export const ITEM_SIGNAL_SUMMARY = [
  "핵심 투자 아이템: 트렌치코트, 블레이저 (장수명 + 80년대 재해석)",
  "상의 핵심: 탱크탑/조끼 + 폴로 셔츠 (레이어링 + 프레피)",
  "스포츠 시그널: Football Jersey (2026 월드컵), Tracksuit (레트로)",
];

export const ITEM_KEYWORDS = {
  tier1: {
    label: "Tier 1 — 핵심 필수템 (8개+ 소스)",
    items: [
      { keyword: "Tank Top / Vest", kr: "탱크탑/니트 조끼", sources: 11, theme: "90년대 미니멀, 레이어링", pool: "A" },
      { keyword: "Polo Shirt", kr: "폴로 셔츠", sources: 9, theme: "Clubhouse, New Prep", pool: "A" },
      { keyword: "Trench Coat", kr: "트렌치코트", sources: 8, theme: "Reworked Classics, 80년대", pool: "A" },
      { keyword: "Blazer", kr: "블레이저", sources: 8, theme: "Nu-niforms, Smarten Up", pool: "A" },
      { keyword: "T-Shirt / Graphic Tee", kr: "티셔츠/그래픽", sources: 8, theme: "브르통 스트라이프, 그래픽", pool: "A" },
    ],
  },
  tier2: {
    label: "Tier 2 — 주요 (5~7개 소스)",
    items: [
      { keyword: "Cargo Pants", kr: "카고 팬츠", sources: 7, theme: "Utility, Great Outdoors", pool: "A" },
      { keyword: "Tracksuit / Track Pants", kr: "트랙수트", sources: 6, theme: "Retro Replay, 스포티즘", pool: null },
      { keyword: "Field Jacket", kr: "필드 재킷", sources: 6, theme: "Future Commuter, 워크웨어", pool: null },
      { keyword: "Capri Trousers", kr: "카프리 팬츠", sources: 5, theme: "2010 Revival", pool: null },
      { keyword: "Hoodie", kr: "후디", sources: 5, theme: "Comfort, 프레피 크롭", pool: null },
    ],
  },
  tier3: {
    label: "Tier 3 — 서브 (2~4개 소스)",
    items: [
      { keyword: "Cardigan", kr: "가디건", sources: 4, theme: "레이어링, 프레피", pool: null },
      { keyword: "Resort Shirt", kr: "리조트/캠프 셔츠", sources: 4, theme: "Refined Resort", pool: null },
      { keyword: "Trucker Jacket", kr: "트러커/데님 재킷", sources: 4, theme: "Reworked Classics", pool: null },
      { keyword: "Short Shorts", kr: "숏 쇼츠", sources: 4, theme: "스포티, 페스티벌", pool: null },
      { keyword: "Bomber Jacket", kr: "봄버 재킷", sources: 4, theme: "클래식 아우터", pool: null },
      { keyword: "Camisole / Bralette", kr: "캐미솔/브라렛", sources: 4, theme: "Pretty Feminine", pool: null },
      { keyword: "Anorak", kr: "아노락", sources: 3, theme: "기능성 레이어링", pool: null },
      { keyword: "Football Jersey", kr: "풋볼 저지", sources: 3, theme: "2026 월드컵, 스포츠코어", pool: "B" },
      { keyword: "Statement Mule", kr: "스테이트먼트 뮬", sources: 3, theme: "오피스, 외출용", pool: null },
      { keyword: "Loafer", kr: "로퍼", sources: 2, theme: "Nu-niforms", pool: null },
      { keyword: "Belt Bag", kr: "벨트백", sources: 2, theme: "유틸리티", pool: "B" },
    ],
  },
};

// ─── Style / Macro Themes ────────────────────────────────────
export const STYLE_MACRO = [
  { theme: "City To Beach / Refined Resort", sources: "11+8", keywords: "리조트↔도심 다목적, Modern Mariner", yoy: "+33%", pool: "A" },
  { theme: "Pretty Feminine / Nu Romantic", sources: 11, keywords: "레이스, 러플, 리본, 플로럴", yoy: "+0.8 ppt", pool: "A" },
  { theme: "Clubhouse / New Prep", sources: "13(통합)", keywords: "프레피, 컨트리클럽, 스포티", yoy: null, pool: "A" },
  { theme: "Nu-niforms / Work Experience", sources: "5~6", keywords: "릴랙스 테일러링, 새 출근복", yoy: "+0.5 ppt", pool: "A" },
  { theme: "Reworked Classics", sources: 5, keywords: "클래식 장수명, 현대적 업그레이드", yoy: "+56~87%", pool: "A" },
  { theme: "80s Glamour", sources: 6, keywords: "파워 숄더, 허리 강조, 글래머", yoy: "+1.4 ppt", pool: "A" },
  { theme: "2010 Revival / Indie Sleaze", sources: "런웨이 확인", keywords: "스키니, 브릿팝, Messy Girl", yoy: null, pool: "A" },
];

export const STYLE_NICHE = [
  { theme: "Fandom Foodies / 키치 그래픽", nature: "그래픽/F&B", relevance: "MLB, Youth 그래픽 참고" },
  { theme: "Offline Dating / 아날로그 향수", nature: "라이프스타일", relevance: "그래픽 모티프 참고" },
  { theme: "Haunted Cabaret / Dark Romance", nature: "APAC 여성복", relevance: "캐주얼/스트리트 일부" },
  { theme: "Messy Girl", nature: "소셜/Youth", relevance: "스트리트 세그먼트" },
  { theme: "Scarf Modular Styling", nature: "스윔/리조트", relevance: "액세서리" },
];

export const ERA_REFERENCES = [
  { era: "80년대", runway: "강함", elements: "파워 숄더, 허리 강조, 글래머" },
  { era: "90년대 브릿팝", runway: "중간", elements: "오아시스, 영국 국기, 인디" },
  { era: "2010년대 Indie Sleaze", runway: "부상 중", elements: "스키니, Messy Girl, 반항적" },
  { era: "Y2K", runway: "지속", elements: "아날로그 모티프, CD 플레이어 가방" },
];

export const SPORT_EVENTS = [
  { event: "2026 FIFA 월드컵 (북중미)", timing: "2026", impact: "Football Jersey, Fan-wear" },
  { event: "F1 영화 개봉", timing: "2025", impact: "레이서 그래픽, 모터 디테일" },
  { event: "비접촉 사교 스포츠", timing: "지속", impact: "프레피, 컨트리클럽 미학" },
];

// ─── Data-backed Signals ─────────────────────────────────────
export const SOCIAL_BUZZ = [
  { keyword: "Boho Chic Style", views: "3.29억 뷰", platform: "RedNote" },
  { keyword: "Pretty Feminine (여름 원피스)", views: "2.05억 뷰", platform: "RedNote" },
  { keyword: "Nautical Style Outfit", views: "1.68억 뷰", platform: "RedNote" },
  { keyword: "Halterneck Top", views: "1.47억 뷰", platform: "RedNote" },
  { keyword: "Ruffle Outfits", views: "5,150만 뷰", platform: "RedNote" },
];

export const YOY_GROWTH = [
  { keyword: "Elegant Simplicity", growth: "+230%", basis: "캣워크 포스트" },
  { keyword: "Sculpted Shoulder", growth: "+225%", basis: "파리 패션 피드" },
  { keyword: "Polka Dot", growth: "+155%", basis: "패션 피드" },
  { keyword: "Preppy Stripes", growth: "+148%", basis: "패션 피드" },
  { keyword: "Pyjama Dressing", growth: "+112%", basis: "남녀 피드 통합" },
  { keyword: "Reworked Classics", growth: "+56~87%", basis: "피드" },
  { keyword: "City To Beach", growth: "+33%", basis: "피드" },
];

export const COLLECTION_SHARE = [
  { keyword: "Joyous Brights (밝은 컬러)", change: "+3.1~4.8 ppt" },
  { keyword: "80s", change: "+1.4 ppt" },
  { keyword: "Lace", change: "+1.2 ppt" },
  { keyword: "Pretty Feminine", change: "+0.8 ppt" },
  { keyword: "Officewear", change: "+0.5 ppt" },
];

// ─── F&F Brand Relevance ─────────────────────────────────────
export const BRAND_RELEVANCE = [
  { trend: "New Prep / Clubhouse", brands: "MLB, Youth", relevance: "high", note: "폴로, 프레피 — 직접 해당" },
  { trend: "Refined Resort", brands: "Descente, NorthFace", relevance: "high", note: "아웃도어↔리조트 크로스" },
  { trend: "Reworked Classics", brands: "Descente, FILA", relevance: "high", note: "클래식 스포츠 아이템 재해석" },
  { trend: "Statement Reds", brands: "MLB, Marithe", relevance: "medium", note: "포인트 컬러 기획" },
  { trend: "Cargo / Utility", brands: "NorthFace, Kolon Sport", relevance: "high", note: "아웃도어 유틸리티" },
  { trend: "Football Jersey", brands: "MLB", relevance: "medium", note: "스포츠코어 — 월드컵 연계" },
  { trend: "Pretty Feminine", brands: "Marithe, Mardi", relevance: "medium", note: "여성 캐주얼 라인" },
  { trend: "80s Shoulder", brands: "Lemaire (럭셔리)", relevance: "low", note: "테일러링 라인" },
  { trend: "Oversized / Wide", brands: "전체", relevance: "high", note: "기본 핏 — 이미 시장 반영" },
];

// ─── Pool A/B ────────────────────────────────────────────────
export const POOL_A = {
  description: "런웨이 캣워크 분석 리포트에서 직접 언급된 키워드 (49개)",
  categories: {
    컬러: "Statement Reds, Berry Tones, Optic White, Gelato Pastels",
    소재: "Sheer, Lace, Denim, Leather",
    실루엣: "Wide Leg, Straight Leg, Sculpted Shoulder, Barrel Leg, Skinny (재테스트)",
    아이템: "Trench Coat, Blazer, Polo Shirt, Tank Top, Cargo Pants",
    스타일: "Refined Resort, Pretty Feminine, New Prep, 80s, 2010 Revival",
  },
};

export const POOL_B = {
  description: "WGSN 포캐스트, TrendCurve AI, 소셜 데이터 기반 독립 예측 (12개)",
  categories: {
    컬러: "Transformative Teal (COTY — AI/포캐스트), Low Key Luxury 관련 톤",
    소재: "Hemp, Lyocell/Tencel (친환경 포캐스트)",
    스타일: "Fandom Foodies, Offline Dating, Haunted Cabaret, Messy Girl",
    아이템: "Football Jersey (2026 월드컵 예측), Belt Bag",
    데이터: "Boho Chic Style (소셜 버즈), Nautical Style (RedNote)",
  },
};
