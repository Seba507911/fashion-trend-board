import {
  COLOR_SIGNAL_SUMMARY, COLOR_KEYWORDS,
  MATERIAL_SIGNAL_SUMMARY, MATERIAL_KEYWORDS,
  SILHOUETTE_SIGNAL_SUMMARY, SILHOUETTE_KEYWORDS,
  ITEM_SIGNAL_SUMMARY, ITEM_KEYWORDS,
  STYLE_MACRO, STYLE_NICHE, ERA_REFERENCES, SPORT_EVENTS,
  SOCIAL_BUZZ, YOY_GROWTH, COLLECTION_SHARE,
} from "../components/expert/reportData";

/* ── 토픽별 WGSN 원문 맥락 ── */
const TOPIC_CONTEXT = {
  color: {
    title: "컬러 시그널",
    icon: "🎨",
    color: "#3266ad",
    narrative: "WGSN은 26SS 시즌을 '미드톤 뉴트럴 베이스 위에 Statement Red가 강렬한 포인트를 찍는 시즌'으로 진단했다. 특히 Cherry Lacquer, Lava Red, Robust Red 등 레드 계열이 3개 이상 독립 키워드로 등장하며 단일 컬러군 중 가장 높은 합의를 보였다. 반면 파스텔은 Blue Aura(13개 소스)를 필두로 Gelato Pastels 그룹이 부상하며, 강렬함과 부드러움의 이중 구조가 형성되었다.",
    wgsnQuotes: [
      { keyword: "Statement Reds", quote: "Cherry Lacquer, Lava Red, Crimson — 레드 계열이 시즌 포인트 컬러의 지배적 위치를 차지. 에너지와 자신감의 표현으로 전 복종에서 채택.", sources: "8~10개 소스 합의" },
      { keyword: "Gelato Pastels", quote: "Blue Aura(13), Peach Jelly(8), Jelly Mint(8) — 부드러운 아이스크림 톤의 파스텔 그룹. 여름 시즌 핵심 포인트.", sources: "8~13개 소스" },
      { keyword: "Transformative Teal", quote: "WGSN+Coloro 선정 2026 올해의 컬러(COTY). '자연과 기술의 균형'을 상징. 런웨이 확인은 제한적이나 포캐스트 독립 예측으로 주목.", sources: "10개 소스 (AI/포캐스트)" },
      { keyword: "뉴트럴 베이스", quote: "Classic Beige, Chalk, Future Grey — 시즌 전체를 관통하는 뉴트럴 미드톤 베이스. Statement 컬러의 배경이자 그 자체로 '조용한 럭셔리' 표현.", sources: "8~9개 소스" },
    ],
    vlmLink: "VLM 분석에서 navy, black, beige, red 등 베이스 컬러 출현 빈도와 비교 가능. Statement Red 계열의 런웨이 출현 빈도를 정량 확인할 수 있음.",
    celebLink: "셀럽의 레드 컬러 착용 빈도와 시점을 추적하면, WGSN 예측 → 런웨이 → 셀럽 채택의 시간축 증명이 가능.",
  },
  material: {
    title: "소재 시그널",
    icon: "🧵",
    color: "#D97706",
    narrative: "시어(투명)와 레이스가 각각 11개 소스에서 언급되며 시즌 소재의 양대 축을 형성했다. WGSN은 이를 '관능미와 여성성의 귀환'으로 해석하면서도, 동시에 Cotton, Linen, Hemp 등 친환경 천연섬유가 기반 소재로 자리잡은 점을 강조했다. 질감 측면에서는 크링클, 해머드 등 3D 텍스처가 은은하게 부상.",
    wgsnQuotes: [
      { keyword: "Sheer / 투명", quote: "시폰, 오간자 중심의 투명 소재가 레이어링과 Day-to-Night 활용으로 가장 지배적인 패브릭으로 부상. 관능미와 여성성을 동시에 전달.", sources: "11개 소스" },
      { keyword: "Lace / 레이스", quote: "Pretty Feminine과 Dark Romance 양방향에서 활용. 전통적 여성성을 넘어 젠더리스 맥락에서도 재해석.", sources: "11개 소스" },
      { keyword: "Leather / 레더", quote: "광택/무광 다양한 질감으로 아우터와 하의에 활용. 럭셔리 시그널이자 시즌리스 투자 아이템.", sources: "7개 소스" },
      { keyword: "친환경 천연섬유", quote: "Cotton(BCI/GOTS 인증), Linen(리조트), Hemp(혼방), Tencel(드레이프) — 지속가능성이 기본값으로 자리잡은 소재군.", sources: "4~7개 소스" },
    ],
    vlmLink: "VLM이 런웨이에서 감지한 sheer, lace, leather 빈도와 WGSN 예측 순위 비교. 특히 시어의 브랜드별 채택률(팀 분석: 20/33)과 교차 검증.",
    celebLink: "셀럽의 시어/레이스 착용 사례를 추적하면, 소재 트렌드의 럭셔리→스트리트 전파 경로 확인 가능.",
  },
  silhouette: {
    title: "실루엣 시그널",
    icon: "📐",
    color: "#059669",
    narrative: "오버사이즈/릴랙스드가 30개 이상 소스에서 언급되며 압도적 1위를 유지하고 있으나, 주목할 것은 Sculpted Shoulder(+225% YoY)의 급부상과 Skinny의 재등장(2010 Revival)이다. 상의는 파워 숄더+허리 강조, 하의는 와이드~배럴 레그라는 양대 산맥이 형성되면서, 단순한 오버사이즈 시대에서 보다 구조적인 실루엣으로의 전환이 감지된다.",
    wgsnQuotes: [
      { keyword: "Sculpted Shoulder / 파워 숄더", quote: "80년대 글래머의 핵심 요소. 캣워크 포스트 기준 +225% YoY 성장. 허리 강조와 결합해 시즌 지배 프로포션 형성.", sources: "14개 소스, +225% YoY" },
      { keyword: "Barrel Leg / 벌룬", quote: "와이드를 넘어 곡선형으로 진화하는 하의 실루엣. 신규 부상 키워드로 12개 소스에서 독립적으로 언급.", sources: "12개 소스 (신규)" },
      { keyword: "Skinny / Slim 재부상", quote: "2010 Revival / Indie Sleaze 트렌드와 연동. 스키니의 재테스트가 11개 소스에서 언급. 와이드 피로감의 반작용.", sources: "11개 소스" },
      { keyword: "Cropped", quote: "상의와 아우터의 기장 단축. 미드리프 노출이 보편적 신체 언어로 자리잡으며 크롭탑/브라렛이 기저 레이어화.", sources: "15개 소스" },
    ],
    vlmLink: "VLM의 oversized, wide, slim, crop 감지 빈도와 시즌별 변화를 비교하면 실루엣 전환점을 정량 확인 가능. 특히 파워 숄더의 런웨이 출현 빈도가 핵심.",
    celebLink: "셀럽의 실루엣 선택(오버사이즈 vs 슬림)이 런웨이 시그널을 따르는지 시간축 추적 가능. 스키니 재부상의 셀럽 채택 시점이 특히 주목.",
  },
  item: {
    title: "아이템 시그널",
    icon: "👔",
    color: "#8B5CF6",
    narrative: "탱크탑/조끼(11개 소스)가 아이템 1위를 차지한 것은 크롭+레이어링 트렌드와 맥락을 같이한다. 트렌치코트와 블레이저(각 8개 소스)는 '리워크드 클래식'으로서 장수명+80년대 재해석이라는 이중 가치를 지닌다. 스포츠 측면에서는 2026 월드컵을 앞두고 Football Jersey가 니치 시그널로 등장.",
    wgsnQuotes: [
      { keyword: "Tank Top / Vest", quote: "90년대 미니멀리즘의 레이어링 필수 아이템. 니트 조끼 포함, 단독 착용에서 레이어링 베이스까지 다목적 활용.", sources: "11개 소스" },
      { keyword: "Trench Coat", quote: "Reworked Classics의 대표 아이템. 80년대 재해석 + 장수명 투자 아이템으로 포지셔닝. 크롭/오버사이즈 변형 다양.", sources: "8개 소스" },
      { keyword: "Polo Shirt", quote: "Clubhouse / New Prep 테마의 핵심 아이템. 프레피 리바이벌과 컨트리클럽 미학을 이끄는 상징적 피스.", sources: "9개 소스" },
      { keyword: "Football Jersey", quote: "2026 FIFA 월드컵(북중미) 연계 스포츠코어 아이템. 니치이지만 이벤트 연동 타이밍이 명확해 기획 근거가 강함.", sources: "3개 소스 (이벤트 연동)" },
    ],
    vlmLink: "VLM에서 감지된 item 태그(bag, shoe, jacket 등)와 WGSN 아이템 키워드를 매칭. 특히 트렌치코트, 블레이저의 런웨이 출현 빈도 확인.",
    celebLink: "셀럽의 아이템 선택(특히 트렌치, 폴로)이 WGSN 예측과 시간적으로 어떻게 연결되는지가 전파 증명의 핵심 사례가 될 수 있음.",
  },
  style: {
    title: "스타일 / 매크로 테마",
    icon: "✨",
    color: "#DC2626",
    narrative: "7개 매크로 테마 중 City To Beach / Refined Resort(11+8개 소스)가 최다 합의. Pretty Feminine(레이스, 러플, 리본)이 +0.8ppt 컬렉션 점유율 증가를 보이며 부상 중. 가장 주목할 성장은 80s Glamour(+1.4ppt)와 Sculpted Shoulder(+225%)로, 미니멀-오버사이즈 사이클의 종료와 글래머의 귀환을 시사한다. 2010 Revival(Indie Sleaze, 스키니)은 런웨이에서 이미 확인되어 다음 시즌으로의 확장이 예상된다.",
    wgsnQuotes: [
      { keyword: "Pretty Feminine / Nu Romantic", quote: "레이스, 러플, 리본, 플로럴 — 관능적 여성성의 귀환. 컬렉션 점유율 +0.8ppt 성장. 시어/레이스 소재와 직접 연동.", sources: "11개 소스, +0.8 ppt" },
      { keyword: "80s Glamour", quote: "파워 숄더, 허리 강조, 글래머 미학. 컬렉션 점유율 +1.4ppt로 가장 빠른 성장세. Sculpted Shoulder(+225%)가 구체적 표현.", sources: "6개 소스, +1.4 ppt" },
      { keyword: "2010 Revival / Indie Sleaze", quote: "스키니 재부상, 브릿팝, Messy Girl — 런웨이에서 이미 확인됨. 오버사이즈 피로감에 대한 반작용으로 해석.", sources: "런웨이 확인" },
      { keyword: "Reworked Classics", quote: "클래식 아이템(트렌치, 블레이저, 데님)을 현대적으로 업그레이드. +56~87% YoY 성장. 장수명 투자 아이템으로서의 가치.", sources: "5개 소스, +56~87%" },
    ],
    vlmLink: "VLM 분석의 overall_silhouette, dominant_colors와 매크로 테마를 매칭하면 '80s Glamour가 실제로 런웨이에서 얼마나 반영되었는가'를 정량 확인 가능.",
    celebLink: "Pretty Feminine(레이스+러플) 스타일링과 80s Glamour(파워 숄더) 착용을 셀럽에서 추적하면, 매크로 테마별 전파 속도 차이를 비교할 수 있음.",
  },
};

function TopicSection({ topicKey }) {
  const t = TOPIC_CONTEXT[topicKey];
  return (
    <section className="mb-12 scroll-mt-20" id={topicKey}>
      {/* Header */}
      <div className="flex items-center gap-2 mb-1">
        <span className="text-xl">{t.icon}</span>
        <h2 className="text-lg font-bold" style={{ color: t.color }}>{t.title}</h2>
      </div>
      <div className="h-0.5 w-12 rounded mb-4" style={{ backgroundColor: t.color }} />

      {/* WGSN 분석 요약 */}
      <div className="bg-white border border-[var(--color-border)] rounded-lg p-5 mb-4">
        <div className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-2">WGSN 분석 요약</div>
        <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">{t.narrative}</p>
      </div>

      {/* 주요 키워드 + 원문 맥락 */}
      <div className="space-y-3 mb-4">
        {t.wgsnQuotes.map((q, i) => (
          <div key={i} className="bg-white border-l-3 rounded-r-lg p-4" style={{ borderLeftColor: t.color, borderLeftWidth: "3px", borderTop: "1px solid var(--color-border)", borderRight: "1px solid var(--color-border)", borderBottom: "1px solid var(--color-border)" }}>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-sm font-bold" style={{ color: t.color }}>{q.keyword}</span>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-gray-100 text-[var(--color-text-muted)]">{q.sources}</span>
            </div>
            <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed italic">"{q.quote}"</p>
          </div>
        ))}
      </div>

      {/* 연계 분석 포인트 */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-blue-50/50 border border-blue-200 rounded-lg p-3">
          <div className="text-[10px] font-semibold text-blue-700 uppercase tracking-wide mb-1">↔ VLM 런웨이 분석 연계</div>
          <p className="text-[11px] text-blue-900 leading-relaxed">{t.vlmLink}</p>
        </div>
        <div className="bg-purple-50/50 border border-purple-200 rounded-lg p-3">
          <div className="text-[10px] font-semibold text-purple-700 uppercase tracking-wide mb-1">→ 셀럽/인플루언서 연계</div>
          <p className="text-[11px] text-purple-900 leading-relaxed">{t.celebLink}</p>
        </div>
      </div>
    </section>
  );
}

export default function ExpertReview() {
  return (
    <main className="flex-1 overflow-y-auto bg-[var(--color-bg)]">
      <div className="max-w-[960px] mx-auto px-8 py-10">

        {/* Header */}
        <div className="mb-6">
          <h1 className="font-['Lora'] text-xl font-semibold tracking-wide">Expert Review — WGSN 26SS</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            WGSN 77건 리포트 (NotebookLM 분석) · 101개 키워드 · VLM 및 셀럽 데이터와 교차 비교용
          </p>
        </div>

        {/* Purpose Box */}
        <div className="bg-amber-50/50 border border-amber-200 rounded-lg p-4 mb-8">
          <div className="text-xs font-semibold text-amber-800 mb-1">이 페이지의 목적</div>
          <p className="text-xs text-amber-900 leading-relaxed">
            WGSN 전문가 예측 키워드를 <strong>런웨이 AI 이미지 분석(VLM)</strong>과 비교해 상호 보완하고,
            곧 수집될 <strong>셀럽/인플루언서 착용 데이터</strong>와 어떻게 연계하여 트렌드 전파를 증명할 것인지의 기준점을 제공합니다.
          </p>
        </div>

        {/* Quick Nav */}
        <div className="flex gap-2 flex-wrap mb-8">
          {Object.entries(TOPIC_CONTEXT).map(([key, t]) => (
            <a key={key} href={`#${key}`} className="text-xs px-3 py-1.5 rounded-full border border-[var(--color-border)] hover:border-current transition-colors" style={{ color: t.color }}>
              {t.icon} {t.title}
            </a>
          ))}
          <a href="#data" className="text-xs px-3 py-1.5 rounded-full border border-[var(--color-border)] text-[#6366F1] hover:border-current transition-colors">
            📊 데이터 시그널
          </a>
        </div>

        {/* Topic Sections */}
        {Object.keys(TOPIC_CONTEXT).map((key) => (
          <TopicSection key={key} topicKey={key} />
        ))}

        {/* ── Data Signals ── */}
        <section id="data" className="mb-12 scroll-mt-20">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xl">📊</span>
            <h2 className="text-lg font-bold text-[#6366F1]">데이터 기반 시그널</h2>
          </div>
          <div className="h-0.5 w-12 rounded mb-4 bg-[#6366F1]" />

          <div className="grid grid-cols-3 gap-4">
            {/* Social Buzz */}
            <div className="bg-white border border-[var(--color-border)] rounded-lg p-4">
              <h4 className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-3">소셜 버즈 (RedNote)</h4>
              <div className="space-y-2.5">
                {SOCIAL_BUZZ.map((s, i) => (
                  <div key={i}>
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-[var(--color-text)] font-medium">{s.keyword}</span>
                      <span className="font-bold text-pink-600 text-[11px]">{s.views}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* YoY Growth */}
            <div className="bg-white border border-[var(--color-border)] rounded-lg p-4">
              <h4 className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-3">YoY 성장률</h4>
              <div className="space-y-2.5">
                {YOY_GROWTH.map((y, i) => (
                  <div key={i}>
                    <div className="flex justify-between text-xs">
                      <span className="text-[var(--color-text)] font-medium">{y.keyword}</span>
                      <span className="font-bold text-emerald-600">{y.growth}</span>
                    </div>
                    <div className="text-[9px] text-[var(--color-text-muted)]">{y.basis}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Collection Share */}
            <div className="bg-white border border-[var(--color-border)] rounded-lg p-4">
              <h4 className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-3">컬렉션 점유율 변화</h4>
              <div className="space-y-2.5">
                {COLLECTION_SHARE.map((c, i) => (
                  <div key={i} className="flex justify-between text-xs">
                    <span className="text-[var(--color-text)] font-medium">{c.keyword}</span>
                    <span className="font-bold text-blue-600">{c.change}</span>
                  </div>
                ))}
              </div>
              <div className="mt-3 pt-2 border-t border-[var(--color-border)]">
                <h4 className="text-[10px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wide mb-2">시대 레퍼런스</h4>
                {ERA_REFERENCES.map((e, i) => (
                  <div key={i} className="flex items-center gap-2 text-[10px] mb-1">
                    <span className={`font-bold ${e.runway === "강함" ? "text-red-600" : e.runway === "부상 중" ? "text-amber-600" : "text-blue-600"}`}>{e.era}</span>
                    <span className="text-[var(--color-text-muted)]">런웨이 {e.runway}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <div className="text-center text-[11px] text-[var(--color-text-muted)] py-4 border-t border-[var(--color-border)]">
          Source: WGSN 77건 리포트 · NotebookLM AI 분석 · 참고용
        </div>
      </div>
    </main>
  );
}
