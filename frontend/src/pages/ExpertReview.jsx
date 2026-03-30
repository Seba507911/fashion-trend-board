import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import SectionReview from "../components/expert/SectionReview";
import {
  SECTIONS,
  COLOR_SIGNAL_SUMMARY, COLOR_KEYWORDS,
  MATERIAL_SIGNAL_SUMMARY, MATERIAL_KEYWORDS,
  SILHOUETTE_SIGNAL_SUMMARY, SILHOUETTE_KEYWORDS,
  ITEM_SIGNAL_SUMMARY, ITEM_KEYWORDS,
  STYLE_MACRO, STYLE_NICHE, ERA_REFERENCES, SPORT_EVENTS,
  SOCIAL_BUZZ, YOY_GROWTH, COLLECTION_SHARE,
  BRAND_RELEVANCE,
  POOL_A, POOL_B,
} from "../components/expert/reportData";
import { useSectionReviews, useSectionReview } from "../hooks/useExpertKeywords";

// ─── Utility Components ──────────────────────────────────────

function SectionAnchor({ id }) {
  return <div id={id} className="scroll-mt-20" />;
}

function SectionHeader({ title, subtitle }) {
  return (
    <div className="mb-6">
      <h2 className="text-xl font-bold text-[var(--color-text)]">{title}</h2>
      {subtitle && <p className="text-sm text-[var(--color-text-muted)] mt-1">{subtitle}</p>}
    </div>
  );
}

function Callout({ children, type = "info" }) {
  const styles = {
    info: "border-blue-300 bg-blue-50/50 text-blue-900",
    warn: "border-amber-300 bg-amber-50/50 text-amber-900",
    key: "border-emerald-300 bg-emerald-50/50 text-emerald-900",
  };
  return (
    <div className={`border-l-4 px-4 py-3 rounded-r-lg text-sm leading-relaxed ${styles[type]}`}>
      {children}
    </div>
  );
}

function SignalList({ items }) {
  return (
    <ul className="space-y-1.5 text-sm text-[var(--color-text-secondary)]">
      {items.map((item, i) => (
        <li key={i} className="flex gap-2">
          <span className="text-[var(--color-primary)] mt-0.5 shrink-0">•</span>
          <span dangerouslySetInnerHTML={{ __html: item.replace(/\*\*(.*?)\*\*/g, '<strong class="text-[var(--color-text)]">$1</strong>') }} />
        </li>
      ))}
    </ul>
  );
}

function PoolTag({ pool }) {
  if (!pool) return null;
  const cls = pool === "A"
    ? "bg-indigo-50 text-indigo-700 border-indigo-200"
    : "bg-orange-50 text-orange-700 border-orange-200";
  return <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded border ${cls}`}>풀 {pool}</span>;
}

function KeywordTable({ tier, columns = ["keyword", "sources", "detail", "pool"] }) {
  const items = tier.items;
  return (
    <div className="mb-6">
      <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide mb-2">
        {tier.label} <span className="text-[var(--color-text-muted)] font-normal">({items.length})</span>
      </h4>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-[var(--color-border)]">
              <th className="text-left py-2 pr-3 text-[11px] font-semibold text-[var(--color-text-muted)] uppercase">키워드</th>
              <th className="text-center py-2 px-2 text-[11px] font-semibold text-[var(--color-text-muted)] uppercase w-16">소스</th>
              <th className="text-left py-2 px-3 text-[11px] font-semibold text-[var(--color-text-muted)] uppercase">비고</th>
              <th className="text-center py-2 pl-2 text-[11px] font-semibold text-[var(--color-text-muted)] uppercase w-14">풀</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.keyword} className="border-b border-[var(--color-border)]/50 hover:bg-gray-50/50">
                <td className="py-2 pr-3">
                  <div className="font-medium text-[var(--color-text)]">{item.keyword}</div>
                  {item.kr && <div className="text-[11px] text-[var(--color-text-muted)]">{item.kr}</div>}
                </td>
                <td className="text-center py-2 px-2 text-[var(--color-primary)] font-semibold">{item.sources}</td>
                <td className="py-2 px-3 text-[var(--color-text-secondary)] text-[13px]">
                  {item.theme && <span className="text-[11px] bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded mr-1">{item.theme}</span>}
                  {item.usage && <span className="text-[11px] bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded mr-1">{item.usage}</span>}
                  {item.note && <span>{item.note}</span>}
                </td>
                <td className="text-center py-2 pl-2"><PoolTag pool={item.pool} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Divider() {
  return <hr className="my-10 border-[var(--color-border)]" />;
}

// ─── Main Page ───────────────────────────────────────────────

export default function ExpertReview() {
  const navigate = useNavigate();
  const season = "26SS";
  const [activeSection, setActiveSection] = useState("overview");

  const { data: reviewsData } = useSectionReviews(season);
  const reviews = reviewsData?.reviews || {};
  const reviewMutation = useSectionReview();

  const handleSaveReview = async (data) => {
    await reviewMutation.mutateAsync(data);
  };

  const getReview = (sectionId) => reviews[`${sectionId}_${season}`] || null;

  // Intersection observer for active section tracking
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        }
      },
      { rootMargin: "-20% 0px -70% 0px" }
    );
    SECTIONS.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);

  return (
    <div className="flex h-full overflow-hidden">
      {/* ─── TOC Sidebar ─── */}
      <nav className="w-56 shrink-0 border-r border-[var(--color-border)] overflow-y-auto py-6 px-4 hidden lg:block">
        <h3 className="text-[11px] font-bold text-[var(--color-text-muted)] uppercase tracking-wider mb-4">목차</h3>
        <ul className="space-y-1">
          {SECTIONS.map((s, i) => {
            const review = getReview(s.id);
            const badge = review?.rating === "fit" ? "bg-emerald-400" : review?.rating === "uncertain" ? "bg-amber-400" : review?.rating === "off" ? "bg-red-400" : null;
            return (
              <li key={s.id}>
                <a
                  href={`#${s.id}`}
                  className={`flex items-center gap-2 px-2 py-1.5 rounded text-[12px] transition-colors ${
                    activeSection === s.id
                      ? "bg-[var(--color-primary)]/10 text-[var(--color-primary)] font-semibold"
                      : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)] hover:bg-gray-50"
                  }`}
                >
                  <span className="text-[var(--color-text-muted)] w-4 text-right shrink-0">{i + 1}.</span>
                  <span className="truncate">{s.title}</span>
                  {badge && <span className={`w-2 h-2 rounded-full ${badge} shrink-0 ml-auto`} />}
                </a>
              </li>
            );
          })}
        </ul>

        <div className="mt-6 pt-4 border-t border-[var(--color-border)]">
          <div className="text-[10px] text-[var(--color-text-muted)] space-y-1">
            <div>리뷰 진행: <strong>{Object.keys(reviews).length}</strong> / {SECTIONS.length}</div>
            <div className="flex gap-2 mt-2">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-400" /> 핏함</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-400" /> 애매</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-400" /> 동떨어짐</span>
            </div>
          </div>
        </div>
      </nav>

      {/* ─── Main Content ─── */}
      <main className="flex-1 overflow-y-auto px-8 py-6">
        <div className="max-w-3xl mx-auto">

          {/* Page Title */}
          <div className="mb-10">
            <p className="text-[11px] font-semibold text-[var(--color-primary)] uppercase tracking-wider mb-2">Expert Report Review</p>
            <h1 className="text-2xl font-bold text-[var(--color-text)] leading-snug">
              WGSN 26SS 키워드 분석 리뷰
            </h1>
            <p className="text-sm text-[var(--color-text-secondary)] mt-2 leading-relaxed">
              WGSN 77건 리포트를 NotebookLM으로 분석하여 도출한 <strong>101개 키워드</strong>입니다.
              팀 동료들과 함께 이 분석 결과가 현업 눈높이에 적절한지,
              어떤 영역이 잘 맞고 어떤 영역이 동떨어져 있는지 리뷰해 주세요.
            </p>
            <div className="flex gap-4 mt-4 text-[11px] text-[var(--color-text-muted)]">
              <span>시즌: <strong className="text-[var(--color-text)]">26SS</strong></span>
              <span>소스: <strong className="text-[var(--color-text)]">WGSN 77건</strong></span>
              <span>키워드: <strong className="text-[var(--color-text)]">101개 (5 카테고리)</strong></span>
              <span>분석: <strong className="text-[var(--color-text)]">NotebookLM AI</strong></span>
            </div>
          </div>

          {/* ═══════════════════════════════════════════════════════
              Section 1: 분석 개요
             ═══════════════════════════════════════════════════════ */}
          <SectionAnchor id="overview" />
          <section className="mb-4">
            <SectionHeader title="1. 분석 개요" subtitle="어떤 데이터를 어떻게 분석했는가" />

            <div className="space-y-4 text-sm text-[var(--color-text-secondary)] leading-relaxed">
              <p>
                WGSN이 26SS 시즌에 대해 발행한 <strong className="text-[var(--color-text)]">77건의 리포트</strong>를
                Google NotebookLM에 입력하여 AI 기반 교차분석을 수행했습니다.
                리포트에는 시즌 컬러 포캐스트, 소재 트렌드, 실루엣 가이드, 키 아이템 추천, 매크로 테마 분석이 포함됩니다.
              </p>

              <Callout type="info">
                <strong>분석 방법</strong>: 77건의 PDF를 NotebookLM에 업로드 → "26SS에서 가장 자주 언급되는 키워드와 테마를 카테고리별로 정리하라" 프롬프트 →
                AI가 교차 빈도 분석 → 수작업 검증 및 Tier/Pool 분류
              </Callout>

              <p>
                이 방법으로 도출된 <strong className="text-[var(--color-text)]">101개 키워드</strong>를
                5개 카테고리(컬러 28, 소재 20, 실루엣 18, 아이템 21, 스타일 14)로 분류하고,
                언급 빈도에 따라 Tier 1(핵심 합의) ~ Tier 4(니치)로 등급을 매겼습니다.
              </p>

              <Callout type="key">
                <strong>핵심 발견 5가지</strong>
                <ol className="mt-2 space-y-1 list-decimal list-inside">
                  <li><strong>Statement Reds</strong> — 레드 계열이 가장 많은 소스(8~13개)에서 언급. 시즌 포인트 컬러.</li>
                  <li><strong>Sheer + Lace</strong> — 투명 소재와 레이스가 시즌 양대 소재. Pretty Feminine 테마 주도.</li>
                  <li><strong>Oversized → Wide</strong> — 릴랙스드/와이드가 여전히 메가 트렌드(30+ 소스). 하지만 Skinny 재부상 신호.</li>
                  <li><strong>Sculpted Shoulder</strong> — 파워 숄더 +225% YoY 급상승. 80년대 글래머 부활.</li>
                  <li><strong>2010 Revival</strong> — 스키니, 카프리, 로우라이즈의 재테스트가 진행 중.</li>
                </ol>
              </Callout>

              <Callout type="warn">
                <strong>리뷰 질문</strong>: 이 분석 방법(NotebookLM AI 교차분석)과 결과 수준이
                패션 현업 팀원의 눈높이에 적절한가요?
                키워드 선정이 너무 광범위하거나, 반대로 빠진 게 있진 않은가요?
              </Callout>
            </div>

            <SectionReview sectionId="overview" season={season} savedReview={getReview("overview")} onSave={handleSaveReview} />
          </section>

          <Divider />

          {/* ═══════════════════════════════════════════════════════
              Section 2: 컬러 시그널
             ═══════════════════════════════════════════════════════ */}
          <SectionAnchor id="color" />
          <section className="mb-4">
            <SectionHeader title="2. 컬러 시그널" subtitle="28개 키워드 — Statement Reds, Gelato Pastels, 뉴트럴 베이스" />

            <div className="space-y-4 text-sm text-[var(--color-text-secondary)] leading-relaxed mb-6">
              <p>
                컬러는 가장 많은 키워드(28개)가 도출된 카테고리입니다.
                전체적인 톤은 <strong className="text-[var(--color-text)]">미드톤/뉴트럴 베이스 위에
                Statement Red 포인트</strong>를 얹는 구조이며,
                파스텔 계열에서는 Gelato Pastels(Blue Aura, Peach Jelly, Jelly Mint)가 새 시그널입니다.
              </p>

              <Callout type="key">
                <strong>주목 포인트</strong>: Transformative Teal이 <strong>2026 올해의 컬러(COTY)</strong>로
                WGSN+Coloro가 공동 선정했습니다. 하지만 이 컬러는 런웨이에서 아직 광범위하게 확인되지 않아
                <strong> 풀 B(전문가 독립 예측)</strong>로 분류했습니다. 실제 마켓에서 이 컬러가 의미 있을지 리뷰가 필요합니다.
              </Callout>

              <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide">시그널 요약</h4>
              <SignalList items={COLOR_SIGNAL_SUMMARY} />
            </div>

            <KeywordTable tier={COLOR_KEYWORDS.tier1} />
            <KeywordTable tier={COLOR_KEYWORDS.tier2} />
            <KeywordTable tier={COLOR_KEYWORDS.tier3} />

            <Callout type="warn">
              <strong>리뷰 질문</strong>: 컬러 분석에서 빠진 키컬러가 있나요?
              Statement Reds가 4개(Cherry Lacquer, Lava Red, Robust Red, Crimson)인데 이들을 하나로 묶어야 할까요?
              Transformative Teal이 F&F 브랜드에서 실제로 쓸 만한 컬러인가요?
            </Callout>

            <SectionReview sectionId="color" season={season} savedReview={getReview("color")} onSave={handleSaveReview} />
          </section>

          <Divider />

          {/* ═══════════════════════════════════════════════════════
              Section 3: 소재 시그널
             ═══════════════════════════════════════════════════════ */}
          <SectionAnchor id="material" />
          <section className="mb-4">
            <SectionHeader title="3. 소재 시그널" subtitle="20개 키워드 — Sheer+Lace 양대 지배, 친환경 천연섬유 기본" />

            <div className="space-y-4 text-sm text-[var(--color-text-secondary)] leading-relaxed mb-6">
              <p>
                소재에서 가장 강한 시그널은 <strong className="text-[var(--color-text)]">Sheer(시어)와 Lace(레이스)</strong>로,
                둘 다 11개 소스에서 언급되었습니다. Pretty Feminine과 Dark Romance 테마를 주도하며,
                시폰/오간자 기반의 레이어링이 Day-to-Night 룩의 핵심입니다.
              </p>
              <p>
                기본 바탕 소재로는 친환경 인증(BCI, GOTS) 천연섬유가 강조되며,
                <strong className="text-[var(--color-text)]"> 니트/저지, 코튼, 데님</strong>은
                F&F 브랜드군과 직접적으로 관련이 높습니다.
              </p>

              <Callout type="info">
                <strong>F&F 관련성 참고</strong>: 니트/저지(라운지웨어), 코튼(친환경), 데님(Y2K/오피스)은
                F&F 관련성이 <strong>높음</strong>으로 판단했습니다. 반면 Sheer/Lace는 럭셔리/여성복 중심이라
                F&F 스포츠/캐주얼 브랜드와는 직접 연결이 약할 수 있습니다.
              </Callout>

              <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide">시그널 요약</h4>
              <SignalList items={MATERIAL_SIGNAL_SUMMARY} />
            </div>

            <KeywordTable tier={MATERIAL_KEYWORDS.tier1} />
            <KeywordTable tier={MATERIAL_KEYWORDS.tier2} />
            <KeywordTable tier={MATERIAL_KEYWORDS.tier3} />

            <Callout type="warn">
              <strong>리뷰 질문</strong>: Sheer/Lace가 시즌 최상위 소재인데, 스포츠/캐주얼 브랜드 관점에서
              이 트렌드를 어떻게 해석해야 할까요? 니트/저지, 코튼, 데님의 F&F 관련성 "높음" 판단이 맞나요?
              기능성 소재(리사이클 폴리, 메리노 울 등)가 빠져 있다면 추가가 필요한가요?
            </Callout>

            <SectionReview sectionId="material" season={season} savedReview={getReview("material")} onSave={handleSaveReview} />
          </section>

          <Divider />

          {/* ═══════════════════════════════════════════════════════
              Section 4: 실루엣 시그널
             ═══════════════════════════════════════════════════════ */}
          <SectionAnchor id="silhouette" />
          <section className="mb-4">
            <SectionHeader title="4. 실루엣 시그널" subtitle="18개 키워드 — Oversized 메가, Sculpted Shoulder +225% YoY" />

            <div className="space-y-4 text-sm text-[var(--color-text-secondary)] leading-relaxed mb-6">
              <p>
                실루엣은 가장 뚜렷한 합의가 있는 카테고리입니다.
                <strong className="text-[var(--color-text)]"> Oversized/Relaxed가 30개+ 소스</strong>에서 언급되며
                전 복종에 걸쳐 메가 트렌드로 자리잡았습니다. 하의는 Wide Leg(22)과 Straight Leg(20)이 양분합니다.
              </p>
              <p>
                주목할 변화는 두 가지입니다. 첫째, <strong className="text-[var(--color-text)]">Sculpted Shoulder(파워 숄더)가
                +225% YoY로 급상승</strong>하며 80년대 글래머의 부활을 예고합니다.
                둘째, <strong className="text-[var(--color-text)]">Skinny/Slim이 2010 Revival 흐름에서 재테스트</strong> 중이며,
                카프리(7부)와 로우라이즈도 함께 거론됩니다.
              </p>

              <Callout type="key">
                <strong>실루엣 양대 구도</strong><br />
                상의: 파워 숄더 + 허리 강조 (구조적, 80년대)<br />
                하의: 와이드~배럴 레그 (유기적, 곡선) — 단, Skinny 재부상 주시
              </Callout>

              <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide">시그널 요약</h4>
              <SignalList items={SILHOUETTE_SIGNAL_SUMMARY} />
            </div>

            <KeywordTable tier={SILHOUETTE_KEYWORDS.tier1} />
            <KeywordTable tier={SILHOUETTE_KEYWORDS.tier2} />
            <KeywordTable tier={SILHOUETTE_KEYWORDS.tier3} />
            <KeywordTable tier={SILHOUETTE_KEYWORDS.tier4} />

            <Callout type="warn">
              <strong>리뷰 질문</strong>: Oversized/Wide가 이미 시장에 충분히 반영되어 있다면,
              이 데이터가 "현재 확인"인지 "내년에도 계속"인지 구분이 가능한가요?
              Skinny 재부상이 실제 마켓에서 감지되고 있나요?
              Barrel Leg(곡선 하의)이 F&F 브랜드에서 현실적으로 적용 가능한가요?
            </Callout>

            <SectionReview sectionId="silhouette" season={season} savedReview={getReview("silhouette")} onSave={handleSaveReview} />
          </section>

          <Divider />

          {/* ═══════════════════════════════════════════════════════
              Section 5: 아이템 시그널
             ═══════════════════════════════════════════════════════ */}
          <SectionAnchor id="item" />
          <section className="mb-4">
            <SectionHeader title="5. 아이템 시그널" subtitle="21개 키워드 — 탱크탑/폴로, 트렌치/블레이저, 월드컵 풋볼 저지" />

            <div className="space-y-4 text-sm text-[var(--color-text-secondary)] leading-relaxed mb-6">
              <p>
                아이템에서는 <strong className="text-[var(--color-text)]">탱크탑/니트 조끼(11)와 폴로 셔츠(9)</strong>가
                상위에 올랐습니다. 90년대 미니멀 레이어링과 New Prep 테마가 배경입니다.
                아우터에서는 트렌치코트(8)와 블레이저(8)가 장수명 + 80년대 재해석 아이템으로 주목됩니다.
              </p>

              <Callout type="key">
                <strong>스포츠 이벤트 연결</strong>: 2026 FIFA 월드컵(북중미)이 열리면서
                Football Jersey(풋볼 저지)가 스포츠코어 아이템으로 부상 중입니다.
                MLB 등 스포츠 브랜드에 직접적인 기회가 될 수 있습니다.
              </Callout>

              <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide">시그널 요약</h4>
              <SignalList items={ITEM_SIGNAL_SUMMARY} />

              {/* Sport events inline */}
              <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide mt-4">스포츠 이벤트 연결</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-[var(--color-border)]">
                      <th className="text-left py-2 pr-3 text-[11px] font-semibold text-[var(--color-text-muted)]">이벤트</th>
                      <th className="text-left py-2 px-3 text-[11px] font-semibold text-[var(--color-text-muted)]">시기</th>
                      <th className="text-left py-2 px-3 text-[11px] font-semibold text-[var(--color-text-muted)]">패션 영향</th>
                    </tr>
                  </thead>
                  <tbody>
                    {SPORT_EVENTS.map((e) => (
                      <tr key={e.event} className="border-b border-[var(--color-border)]/50">
                        <td className="py-2 pr-3 font-medium text-[var(--color-text)]">{e.event}</td>
                        <td className="py-2 px-3 text-[var(--color-text-secondary)]">{e.timing}</td>
                        <td className="py-2 px-3 text-[var(--color-text-secondary)]">{e.impact}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <KeywordTable tier={ITEM_KEYWORDS.tier1} />
            <KeywordTable tier={ITEM_KEYWORDS.tier2} />
            <KeywordTable tier={ITEM_KEYWORDS.tier3} />

            <Callout type="warn">
              <strong>리뷰 질문</strong>: 탱크탑/폴로 셔츠의 상위 랭킹이 실제 리테일 수요와 일치하나요?
              트렌치코트/블레이저가 스포츠/캐주얼 브랜드에서도 의미가 있을까요?
              풋볼 저지의 월드컵 연계 — 타이밍과 물량 기획에 반영할 수 있는 수준인가요?
            </Callout>

            <SectionReview sectionId="item" season={season} savedReview={getReview("item")} onSave={handleSaveReview} />
          </section>

          <Divider />

          {/* ═══════════════════════════════════════════════════════
              Section 6: 스타일 / 매크로 테마
             ═══════════════════════════════════════════════════════ */}
          <SectionAnchor id="style" />
          <section className="mb-4">
            <SectionHeader title="6. 스타일 / 매크로 테마" subtitle="7개 합의 테마 + 5개 니치 예측 + 시대 레퍼런스" />

            <div className="space-y-4 text-sm text-[var(--color-text-secondary)] leading-relaxed mb-6">
              <p>
                스타일 테마는 크게 <strong className="text-[var(--color-text)]">전 리포트 공통 합의(7개)</strong>와
                <strong className="text-[var(--color-text)]"> 소수 리포트 독립 예측(5개)</strong>으로 나뉩니다.
                합의 테마 중 City To Beach(+33% YoY)와 Pretty Feminine(+0.8 ppt 점유율)이
                데이터 기반으로도 확인되는 가장 강력한 시그널입니다.
              </p>

              <Callout type="info">
                <strong>시대 레퍼런스 맥락</strong>: 패션 트렌드는 보통 20~30년 주기로 과거를 재해석합니다.
                현재 80년대(파워 숄더, 글래머), 90년대(브릿팝, 인디), 2010년대(스키니, Indie Sleaze)가
                동시에 재소환되고 있으며, Y2K도 아직 잔류 중입니다.
                이 "과거 재해석의 동시 다발"이 26SS의 특징적인 현상입니다.
              </Callout>
            </div>

            {/* Macro themes table */}
            <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide mb-2">전 리포트 공통 합의 (Macro Consensus)</h4>
            <div className="overflow-x-auto mb-6">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="border-b border-[var(--color-border)]">
                    <th className="text-left py-2 pr-3 text-[11px] font-semibold text-[var(--color-text-muted)]">테마</th>
                    <th className="text-center py-2 px-2 text-[11px] font-semibold text-[var(--color-text-muted)] w-16">소스</th>
                    <th className="text-left py-2 px-3 text-[11px] font-semibold text-[var(--color-text-muted)]">핵심 키워드</th>
                    <th className="text-center py-2 px-2 text-[11px] font-semibold text-[var(--color-text-muted)] w-16">YoY</th>
                    <th className="text-center py-2 pl-2 text-[11px] font-semibold text-[var(--color-text-muted)] w-14">풀</th>
                  </tr>
                </thead>
                <tbody>
                  {STYLE_MACRO.map((s) => (
                    <tr key={s.theme} className="border-b border-[var(--color-border)]/50 hover:bg-gray-50/50">
                      <td className="py-2 pr-3 font-medium text-[var(--color-text)]">{s.theme}</td>
                      <td className="text-center py-2 px-2 text-[var(--color-primary)] font-semibold">{s.sources}</td>
                      <td className="py-2 px-3 text-[var(--color-text-secondary)] text-[13px]">{s.keywords}</td>
                      <td className="text-center py-2 px-2 text-emerald-600 font-medium text-[12px]">{s.yoy || "—"}</td>
                      <td className="text-center py-2 pl-2"><PoolTag pool={s.pool} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Niche predictions */}
            <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide mb-2">소수 리포트 독립 예측 (Niche Predictions)</h4>
            <div className="overflow-x-auto mb-6">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="border-b border-[var(--color-border)]">
                    <th className="text-left py-2 pr-3 text-[11px] font-semibold text-[var(--color-text-muted)]">테마</th>
                    <th className="text-left py-2 px-3 text-[11px] font-semibold text-[var(--color-text-muted)]">성격</th>
                    <th className="text-left py-2 px-3 text-[11px] font-semibold text-[var(--color-text-muted)]">F&F 관련성</th>
                  </tr>
                </thead>
                <tbody>
                  {STYLE_NICHE.map((s) => (
                    <tr key={s.theme} className="border-b border-[var(--color-border)]/50 hover:bg-gray-50/50">
                      <td className="py-2 pr-3 font-medium text-[var(--color-text)]">{s.theme}</td>
                      <td className="py-2 px-3 text-[var(--color-text-secondary)]">{s.nature}</td>
                      <td className="py-2 px-3 text-[var(--color-text-secondary)]">{s.relevance}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Era references */}
            <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide mb-2">시대적 레퍼런스</h4>
            <div className="overflow-x-auto mb-6">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="border-b border-[var(--color-border)]">
                    <th className="text-left py-2 pr-3 text-[11px] font-semibold text-[var(--color-text-muted)]">시대</th>
                    <th className="text-center py-2 px-3 text-[11px] font-semibold text-[var(--color-text-muted)]">런웨이 반영</th>
                    <th className="text-left py-2 px-3 text-[11px] font-semibold text-[var(--color-text-muted)]">핵심 요소</th>
                  </tr>
                </thead>
                <tbody>
                  {ERA_REFERENCES.map((e) => (
                    <tr key={e.era} className="border-b border-[var(--color-border)]/50">
                      <td className="py-2 pr-3 font-medium text-[var(--color-text)]">{e.era}</td>
                      <td className="text-center py-2 px-3">
                        <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium ${
                          e.runway === "강함" ? "bg-emerald-50 text-emerald-700" :
                          e.runway === "중간" ? "bg-amber-50 text-amber-700" :
                          "bg-blue-50 text-blue-700"
                        }`}>{e.runway}</span>
                      </td>
                      <td className="py-2 px-3 text-[var(--color-text-secondary)]">{e.elements}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <Callout type="warn">
              <strong>리뷰 질문</strong>: 7개 합의 테마 중 F&F 브랜드에 직접 적용 가능한 것은?
              New Prep/Clubhouse가 MLB, Youth에 "직접 해당"이라 판단했는데 동의하시나요?
              니치 예측(Fandom Foodies, Messy Girl 등)은 무시해도 되는 수준인가요, 참고할 가치가 있나요?
            </Callout>

            <SectionReview sectionId="style" season={season} savedReview={getReview("style")} onSave={handleSaveReview} />
          </section>

          <Divider />

          {/* ═══════════════════════════════════════════════════════
              Section 7: 데이터 기반 시그널
             ═══════════════════════════════════════════════════════ */}
          <SectionAnchor id="data" />
          <section className="mb-4">
            <SectionHeader title="7. 데이터 기반 시그널" subtitle="소셜 버즈, YoY 급상승, 컬렉션 점유율 — 정량 근거" />

            <div className="space-y-4 text-sm text-[var(--color-text-secondary)] leading-relaxed mb-6">
              <p>
                WGSN 리포트에 포함된 정량 데이터입니다. 소셜 미디어 버즈(RedNote 조회수),
                전년 대비 급상승 키워드, 컬렉션 내 점유율 변화를 통해
                <strong className="text-[var(--color-text)]"> 어떤 트렌드가 이미 대중적 관심을 받고 있고,
                어떤 트렌드가 디자이너 채택 단계인지</strong> 구분할 수 있습니다.
              </p>

              <Callout type="info">
                <strong>데이터 해석 참고</strong>: 소셜 버즈가 높다고 반드시 좋은 트렌드는 아닙니다.
                Boho Chic(3.29억 뷰)는 대중 관심이 높지만, WGSN의 핵심 포캐스트와는 거리가 있을 수 있습니다.
                반면 Sculpted Shoulder(+225% YoY)는 패션 전문 피드에서의 급상승이라 전문가 시그널에 가깝습니다.
              </Callout>
            </div>

            {/* Social buzz */}
            <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide mb-2">소셜 미디어 버즈 (대중 관심도)</h4>
            <div className="overflow-x-auto mb-6">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="border-b border-[var(--color-border)]">
                    <th className="text-left py-2 pr-3 text-[11px] font-semibold text-[var(--color-text-muted)]">키워드</th>
                    <th className="text-right py-2 px-3 text-[11px] font-semibold text-[var(--color-text-muted)]">조회수</th>
                    <th className="text-left py-2 pl-3 text-[11px] font-semibold text-[var(--color-text-muted)]">플랫폼</th>
                  </tr>
                </thead>
                <tbody>
                  {SOCIAL_BUZZ.map((s) => (
                    <tr key={s.keyword} className="border-b border-[var(--color-border)]/50">
                      <td className="py-2 pr-3 font-medium text-[var(--color-text)]">{s.keyword}</td>
                      <td className="text-right py-2 px-3 text-[var(--color-primary)] font-semibold">{s.views}</td>
                      <td className="py-2 pl-3 text-[var(--color-text-secondary)]">{s.platform}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* YoY growth */}
            <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide mb-2">전년 대비 급상승 (트렌드 확산 속도)</h4>
            <div className="overflow-x-auto mb-6">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="border-b border-[var(--color-border)]">
                    <th className="text-left py-2 pr-3 text-[11px] font-semibold text-[var(--color-text-muted)]">키워드</th>
                    <th className="text-right py-2 px-3 text-[11px] font-semibold text-[var(--color-text-muted)]">YoY</th>
                    <th className="text-left py-2 pl-3 text-[11px] font-semibold text-[var(--color-text-muted)]">기준</th>
                  </tr>
                </thead>
                <tbody>
                  {YOY_GROWTH.map((y) => (
                    <tr key={y.keyword} className="border-b border-[var(--color-border)]/50">
                      <td className="py-2 pr-3 font-medium text-[var(--color-text)]">{y.keyword}</td>
                      <td className="text-right py-2 px-3 text-emerald-600 font-bold">{y.growth}</td>
                      <td className="py-2 pl-3 text-[var(--color-text-secondary)]">{y.basis}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Collection share */}
            <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide mb-2">컬렉션 내 점유율 증가 (디자이너 채택)</h4>
            <div className="overflow-x-auto mb-6">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="border-b border-[var(--color-border)]">
                    <th className="text-left py-2 pr-3 text-[11px] font-semibold text-[var(--color-text-muted)]">키워드</th>
                    <th className="text-right py-2 px-3 text-[11px] font-semibold text-[var(--color-text-muted)]">점유율 변화</th>
                  </tr>
                </thead>
                <tbody>
                  {COLLECTION_SHARE.map((c) => (
                    <tr key={c.keyword} className="border-b border-[var(--color-border)]/50">
                      <td className="py-2 pr-3 font-medium text-[var(--color-text)]">{c.keyword}</td>
                      <td className="text-right py-2 px-3 text-emerald-600 font-bold">{c.change}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <Callout type="warn">
              <strong>리뷰 질문</strong>: 이 정량 데이터들이 신뢰할 만한가요?
              RedNote(샤오홍슈) 데이터가 한국 시장에도 유의미한 참고가 되나요?
              YoY 급상승 데이터의 기준(캣워크 포스트, 패션 피드)이 F&F 관점에서 충분한 근거인가요?
            </Callout>

            <SectionReview sectionId="data" season={season} savedReview={getReview("data")} onSave={handleSaveReview} />
          </section>

          <Divider />

          {/* ═══════════════════════════════════════════════════════
              Section 8: F&F 브랜드 관련성
             ═══════════════════════════════════════════════════════ */}
          <SectionAnchor id="brand" />
          <section className="mb-4">
            <SectionHeader title="8. F&F 브랜드 관련성 매핑" subtitle="WGSN 트렌드 → F&F 브랜드 연결 초안" />

            <div className="space-y-4 text-sm text-[var(--color-text-secondary)] leading-relaxed mb-6">
              <p>
                아래는 WGSN 트렌드와 F&F 산하/관련 브랜드의 연결을 1차 정리한 것입니다.
                이 매핑이 <strong className="text-[var(--color-text)]">현업에서 실제로 맞는지,
                빠진 연결이 있는지, 과대평가된 연결이 있는지</strong> 검토해 주세요.
              </p>
            </div>

            <div className="overflow-x-auto mb-6">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="border-b-2 border-[var(--color-border)]">
                    <th className="text-left py-2 pr-3 text-[11px] font-semibold text-[var(--color-text-muted)]">WGSN 트렌드</th>
                    <th className="text-left py-2 px-3 text-[11px] font-semibold text-[var(--color-text-muted)]">F&F 브랜드</th>
                    <th className="text-center py-2 px-3 text-[11px] font-semibold text-[var(--color-text-muted)]">관련성</th>
                    <th className="text-left py-2 pl-3 text-[11px] font-semibold text-[var(--color-text-muted)]">근거</th>
                  </tr>
                </thead>
                <tbody>
                  {BRAND_RELEVANCE.map((b) => (
                    <tr key={b.trend} className="border-b border-[var(--color-border)]/50 hover:bg-gray-50/50">
                      <td className="py-2.5 pr-3 font-medium text-[var(--color-text)]">{b.trend}</td>
                      <td className="py-2.5 px-3">
                        <span className="text-[var(--color-primary)] font-medium">{b.brands}</span>
                      </td>
                      <td className="text-center py-2.5 px-3">
                        <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium ${
                          b.relevance === "high" ? "bg-emerald-50 text-emerald-700 border border-emerald-200" :
                          b.relevance === "medium" ? "bg-amber-50 text-amber-700 border border-amber-200" :
                          "bg-gray-50 text-gray-600 border border-gray-200"
                        }`}>
                          {b.relevance === "high" ? "높음" : b.relevance === "medium" ? "중간" : "낮음"}
                        </span>
                      </td>
                      <td className="py-2.5 pl-3 text-[var(--color-text-secondary)] text-[13px]">{b.note}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <Callout type="warn">
              <strong>리뷰 질문</strong>: 이 브랜드-트렌드 매핑에서 빠진 연결이 있나요?
              예를 들어, Descente × 80s Shoulder, FILA × Tracksuit 등의 추가 연결은?
              "관련성 높음"으로 표시한 항목 중 실제로는 약한 것이 있나요?
            </Callout>

            <SectionReview sectionId="brand" season={season} savedReview={getReview("brand")} onSave={handleSaveReview} />
          </section>

          <Divider />

          {/* ═══════════════════════════════════════════════════════
              Section 9: 풀 A/B 초안 검증
             ═══════════════════════════════════════════════════════ */}
          <SectionAnchor id="pool" />
          <section className="mb-4">
            <SectionHeader title="9. 풀 A/B 초안 검증" subtitle="런웨이 교차검증 전 분류 — 49개 A, 12개 B, 40개 미분류" />

            <div className="space-y-4 text-sm text-[var(--color-text-secondary)] leading-relaxed mb-6">
              <p>
                101개 키워드를 <strong className="text-[var(--color-text)]">풀 A(런웨이에서도 확인)</strong>와
                <strong className="text-[var(--color-text)]"> 풀 B(전문가 독립 예측)</strong>로 초안 분류했습니다.
                이 분류는 WGSN 내부의 런웨이 분석 vs 포캐스트 구분 기반이며,
                <strong className="text-[var(--color-text)]"> 실제 풀 A/B 확정은 FTIB 런웨이 VLM 데이터(11,905 룩)와
                교차검증 후 결정</strong>됩니다.
              </p>

              <Callout type="info">
                <strong>풀 A vs 풀 B의 의미</strong><br />
                <strong>풀 A</strong>: 런웨이 Top 30 ∩ 전문가 리포트 — 디자이너와 전문가가 합의한 시그널. 확산 가능성 높음.<br />
                <strong>풀 B</strong>: 전문가 리포트 − 런웨이 — 전문가만의 독립 예측. 맞으면 선제 대응 가치가 크지만, 빗나갈 수도 있음.
              </Callout>
            </div>

            {/* Pool A */}
            <div className="border border-indigo-200 bg-indigo-50/30 rounded-lg p-5 mb-4">
              <h4 className="text-sm font-bold text-indigo-800 mb-1">풀 A — 런웨이 확인 (49개)</h4>
              <p className="text-[12px] text-indigo-600 mb-3">{POOL_A.description}</p>
              <div className="space-y-2">
                {Object.entries(POOL_A.categories).map(([cat, keywords]) => (
                  <div key={cat} className="flex gap-2 text-sm">
                    <span className="font-semibold text-indigo-700 w-16 shrink-0">{cat}</span>
                    <span className="text-[var(--color-text-secondary)]">{keywords}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Pool B */}
            <div className="border border-orange-200 bg-orange-50/30 rounded-lg p-5 mb-6">
              <h4 className="text-sm font-bold text-orange-800 mb-1">풀 B — 전문가 독립 예측 (12개)</h4>
              <p className="text-[12px] text-orange-600 mb-3">{POOL_B.description}</p>
              <div className="space-y-2">
                {Object.entries(POOL_B.categories).map(([cat, keywords]) => (
                  <div key={cat} className="flex gap-2 text-sm">
                    <span className="font-semibold text-orange-700 w-16 shrink-0">{cat}</span>
                    <span className="text-[var(--color-text-secondary)]">{keywords}</span>
                  </div>
                ))}
              </div>
            </div>

            <Callout type="key">
              <strong>미분류 40개</strong>: 풀 A에도 B에도 명확히 속하지 않는 40개 키워드가 있습니다.
              대부분 뉴트럴 베이스 컬러(Black, Beige, Grey 등)나 기본 소재(Cotton, Linen 등)로,
              "트렌드"라기보다 "기본"에 가깝습니다. 이들을 별도 "기본 풀"로 분리할지,
              아니면 풀 A에 포함시킬지 논의가 필요합니다.
            </Callout>

            <Callout type="warn">
              <strong>리뷰 질문</strong>: 풀 A/B 분류 기준이 적절한가요?
              풀 B의 Transformative Teal(COTY)이 실제로 마켓에서 의미가 있을까요?
              미분류 40개를 어떻게 처리하면 좋을까요?
            </Callout>

            <SectionReview sectionId="pool" season={season} savedReview={getReview("pool")} onSave={handleSaveReview} />
          </section>

          <Divider />

          {/* ═══════════════════════════════════════════════════════
              Section 10: 방법론 & 다음 단계
             ═══════════════════════════════════════════════════════ */}
          <SectionAnchor id="method" />
          <section className="mb-4">
            <SectionHeader title="10. 방법론 & 다음 단계" subtitle="분석 보완 방향과 교차검증 순서 논의" />

            <div className="space-y-4 text-sm text-[var(--color-text-secondary)] leading-relaxed mb-6">
              <p>
                현재 분석은 <strong className="text-[var(--color-text)]">WGSN 단일 소스 + NotebookLM AI 분석</strong>에
                기반합니다. 이 방법의 장단점과 향후 보완 방향을 정리합니다.
              </p>

              <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide">현재 방법의 강점</h4>
              <SignalList items={[
                "**77건 대량 리포트**를 교차분석하여 개별 리포트의 편향을 줄임",
                "**소스 수 기반 Tier 분류**로 합의 수준을 정량화",
                "**풀 A/B 구분**으로 확인된 시그널과 독립 예측을 분리",
              ]} />

              <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide mt-4">한계 및 리스크</h4>
              <SignalList items={[
                "**WGSN 단일 소스** — WGSN 편향이 있을 수 있음. 타 기관(Tagwalk, Pantone, BoF)과 교차 필요",
                "**AI 분석 한계** — NotebookLM이 패션 맥락을 완전히 이해하지 못할 수 있음. 전문가 검증 필수",
                "**정량 ≠ 정성** — 소스 수가 많다고 트렌드가 강한 게 아닐 수 있음. 현업 감각과 대조 필요",
                "**시간차** — WGSN 리포트 발행 시점과 실제 시장 반응 사이의 갭",
              ]} />

              <h4 className="text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wide mt-4">제안하는 다음 단계</h4>
              <div className="space-y-3">
                <div className="flex gap-3 items-start">
                  <span className="bg-[var(--color-primary)] text-white w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold shrink-0">1</span>
                  <div>
                    <div className="font-medium text-[var(--color-text)]">이 리뷰 완료</div>
                    <div className="text-[13px]">팀원들의 섹션별 리뷰를 수집. "당연/흥미/아닌데" 감을 잡음.</div>
                  </div>
                </div>
                <div className="flex gap-3 items-start">
                  <span className="bg-[var(--color-primary)] text-white w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold shrink-0">2</span>
                  <div>
                    <div className="font-medium text-[var(--color-text)]">런웨이 VLM 1차 대조</div>
                    <div className="text-[13px]">풀 A 후보 키워드의 실제 런웨이 등장 빈도 확인 (11,905 룩 × VLM 라벨)</div>
                  </div>
                </div>
                <div className="flex gap-3 items-start">
                  <span className="bg-[var(--color-primary)] text-white w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold shrink-0">3</span>
                  <div>
                    <div className="font-medium text-[var(--color-text)]">Tagwalk 추가 여부 판단</div>
                    <div className="text-[13px]">런웨이 정량 데이터로 풀 A를 확정하고, WGSN과 교차 확인</div>
                  </div>
                </div>
                <div className="flex gap-3 items-start">
                  <span className="bg-[var(--color-primary)] text-white w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold shrink-0">4</span>
                  <div>
                    <div className="font-medium text-[var(--color-text)]">마켓 매칭</div>
                    <div className="text-[13px]">확정된 키워드 → 마켓 상품(11,368개) 교차 검색으로 실제 시장 반영도 측정</div>
                  </div>
                </div>
                <div className="flex gap-3 items-start">
                  <span className="bg-[var(--color-primary)] text-white w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold shrink-0">5</span>
                  <div>
                    <div className="font-medium text-[var(--color-text)]">Vogue/BoF 추가 여부 판단</div>
                    <div className="text-[13px]">에디토리얼 관점 보완 — 특히 셀럽/스트리트 시그널</div>
                  </div>
                </div>
              </div>
            </div>

            <Callout type="warn">
              <strong>리뷰 질문</strong>: 위 다음 단계 순서가 맞나요?
              Tagwalk이나 Vogue/BoF를 먼저 추가해야 한다고 생각하시나요?
              NotebookLM AI 분석 자체에 대한 신뢰도는 어느 정도인가요?
              다른 분석 방법이나 소스가 필요하다면 무엇인가요?
            </Callout>

            <SectionReview sectionId="method" season={season} savedReview={getReview("method")} onSave={handleSaveReview} />
          </section>

          {/* Footer */}
          <div className="mt-12 mb-8 pt-6 border-t border-[var(--color-border)] text-center">
            <p className="text-[11px] text-[var(--color-text-muted)]">
              WGSN 26SS Expert Report Review — FTIB Project
            </p>
            <div className="flex justify-center gap-3 mt-3">
              <button
                onClick={() => navigate("/runway?season=26SS")}
                className="text-[12px] text-[var(--color-primary)] hover:underline"
              >
                런웨이 데이터 보기
              </button>
              <span className="text-[var(--color-text-muted)]">·</span>
              <button
                onClick={() => navigate("/market")}
                className="text-[12px] text-[var(--color-primary)] hover:underline"
              >
                마켓 브랜드 보드
              </button>
              <span className="text-[var(--color-text-muted)]">·</span>
              <button
                onClick={() => navigate("/flow-check")}
                className="text-[12px] text-[var(--color-primary)] hover:underline"
              >
                Trend Flow Check
              </button>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
