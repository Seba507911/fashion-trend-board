import { useState } from "react";

/* ── Runway-led 전파 플로우 ── */

const FLOW_STEPS = [
  {
    id: "runway",
    label: "런웨이 시그널",
    status: "done",
    color: "#3266ad",
    detail: "하이엔드 디자이너 런웨이에서 키워드/아이템 추출",
    data: "TagWalk 13,882 + Vogue 47,519 이미지",
    sub: "AI 이미지 분석 + 쇼 노트 교차 검증으로 트렌드 키워드 도출",
  },
  {
    id: "celeb",
    label: "셀럽 / 인플루언서",
    status: "active",
    color: "#8B5CF6",
    detail: "런웨이 트렌드를 착용하는 셀럽·인플루언서 모니터링",
    data: "셀럽 풀 설정 진행 중",
    sub: "엠배서더 구분, 착용 시점 기록, 영향력 분류 (Top / Mid / Micro)",
  },
  {
    id: "designer",
    label: "디자이너 브랜드",
    status: "upcoming",
    color: "#059669",
    detail: "소규모 디자이너 브랜드에서 트렌드 상품화 확인",
    data: "국내 캐주얼/스트리트 브랜드 중심",
    sub: "런웨이를 직접 참조해 자기 해석으로 빠르게 상품화. 일반인이 구매 가능한 상품의 공급원.",
  },
  {
    id: "sns",
    label: "일반 SNS 확산",
    status: "upcoming",
    color: "#D97706",
    detail: "인스타그램/틱톡/샤오홍수에서 일반인 착용 확산 모니터링",
    data: "타 팀 SNS 수집 데이터 연계 예정",
    sub: "디자이너 브랜드 상품 출시 후 구매·착용한 일반인의 #OOTD 확산으로 대중화 확인.",
  },
];

const STATUS_STYLE = {
  done: { bg: "bg-emerald-500", text: "text-white", label: "완료" },
  active: { bg: "bg-blue-500", text: "text-white", label: "진행 중" },
  upcoming: { bg: "bg-gray-200", text: "text-gray-500", label: "예정" },
};

const WHY_NOT_MASS = [
  { factor: "의사결정 속도", mass: "대조직, 다층 승인", designer: "소수 인력, 빠른 결정" },
  { factor: "생산 리드타임", mass: "6~12개월 (벤더 의뢰)", designer: "1~3개월 (자체/소규모)" },
  { factor: "트렌드 반영", mass: "1~2시즌 지연, 간혹 오해석", designer: "실시간~1시즌, 자기 해석" },
  { factor: "데이터 의미", mass: "생산 사이클 결과", designer: "실제 트렌드 수용/감도" },
];

const SAMPLE_KEYWORDS = [
  { keyword: "레더", runway: "22/33 브랜드", status: "셀럽 검증 중", propagation: 75 },
  { keyword: "시어/트랜스루선트", runway: "20/33 브랜드", status: "셀럽 검증 중", propagation: 65 },
  { keyword: "크롭탑", runway: "19/33 브랜드", status: "SNS 확산 확인", propagation: 80 },
  { keyword: "러플/볼륨", runway: "17/33 브랜드", status: "셀럽 검증 중", propagation: 55 },
  { keyword: "워크웨어", runway: "15/33 브랜드", status: "대기", propagation: 40 },
  { keyword: "오픈백 가방", runway: "AI 감지", status: "마켓 출현 확인", propagation: 70 },
  { keyword: "뾰족한 토 구두", runway: "AI 감지", status: "마켓 출현 확인", propagation: 60 },
];

function FlowDiagram() {
  return (
    <div className="flex items-stretch gap-0 mb-8">
      {FLOW_STEPS.map((step, i) => {
        const st = STATUS_STYLE[step.status];
        return (
          <div key={step.id} className="flex-1 flex items-center">
            <div className={`flex-1 border rounded-xl p-5 ${
              step.status === "done" ? "border-emerald-300 bg-emerald-50/50" :
              step.status === "active" ? "border-blue-300 bg-blue-50/50" :
              "border-[var(--color-border)] bg-white"
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-[11px] font-bold ${st.bg} ${st.text}`}>
                  {step.status === "done" ? "✓" : i + 1}
                </div>
                <span className="text-sm font-bold" style={{ color: step.color }}>{step.label}</span>
              </div>
              <p className="text-xs text-[var(--color-text-secondary)] mb-1">{step.detail}</p>
              <p className="text-[10px] text-[var(--color-text-muted)]">{step.data}</p>
            </div>
            {i < FLOW_STEPS.length - 1 && (
              <div className="text-[var(--color-text-muted)] px-2 text-lg shrink-0">→</div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default function TrendFlow() {
  const [expandWhy, setExpandWhy] = useState(false);

  return (
    <main className="flex-1 overflow-y-auto bg-[var(--color-bg)]">
      <div className="max-w-[1100px] mx-auto px-8 py-10">

        {/* Header */}
        <div className="mb-8">
          <h1 className="font-['Lora'] text-xl font-semibold tracking-wide">Trend Flow</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            Runway-led 트렌드 전파 모니터링 — 런웨이 → 셀럽 → 디자이너 브랜드 → 일반 SNS
          </p>
        </div>

        {/* Flow Diagram */}
        <FlowDiagram />

        {/* Detailed Steps */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          {FLOW_STEPS.map((step) => (
            <div key={step.id} className="bg-white border border-[var(--color-border)] rounded-lg p-5">
              <div className="flex items-center gap-2 mb-3">
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: step.color }} />
                <span className="text-sm font-semibold" style={{ color: step.color }}>{step.label}</span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ml-auto ${
                  step.status === "done" ? "bg-emerald-100 text-emerald-700" :
                  step.status === "active" ? "bg-blue-100 text-blue-700" :
                  "bg-gray-100 text-gray-500"
                }`}>
                  {STATUS_STYLE[step.status].label}
                </span>
              </div>
              <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">{step.sub}</p>
            </div>
          ))}
        </div>

        {/* Why Designer Brands */}
        <div className="bg-white border border-[var(--color-border)] rounded-lg p-5 mb-8">
          <button
            onClick={() => setExpandWhy(!expandWhy)}
            className="w-full text-left flex items-center justify-between"
          >
            <h3 className="text-sm font-semibold text-[var(--color-text)]">
              왜 매스 브랜드가 아닌 디자이너 브랜드인가?
            </h3>
            <span className="text-xs text-[var(--color-text-muted)]">{expandWhy ? "▴" : "▾"}</span>
          </button>
          {expandWhy && (
            <div className="mt-4">
              <p className="text-xs text-[var(--color-text-secondary)] mb-3">
                매스 브랜드(Nike, Zara 등)는 생산 리드타임과 조직 구조 문제로 트렌드 전파 검증에 부적합합니다.
                소규모 디자이너 브랜드가 하이엔드 트렌드를 빠르게 재해석하는 실제 전파 경로를 추적합니다.
              </p>
              <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="border-b border-[var(--color-border)]">
                    <th className="text-left py-2 text-[var(--color-text-muted)]">요인</th>
                    <th className="text-center py-2 text-red-400">매스 브랜드</th>
                    <th className="text-center py-2 text-emerald-600">디자이너 브랜드</th>
                  </tr>
                </thead>
                <tbody>
                  {WHY_NOT_MASS.map((row) => (
                    <tr key={row.factor} className="border-b border-[var(--color-border)]/50">
                      <td className="py-2 font-medium text-[var(--color-text)]">{row.factor}</td>
                      <td className="py-2 text-center text-[var(--color-text-muted)]">{row.mass}</td>
                      <td className="py-2 text-center text-[var(--color-text-secondary)]">{row.designer}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Keyword Tracking Table */}
        <div className="bg-white border border-[var(--color-border)] rounded-lg p-5">
          <h3 className="text-sm font-semibold text-[var(--color-text)] mb-4">
            26SS 핵심 키워드 전파 현황
          </h3>
          <p className="text-xs text-[var(--color-text-muted)] mb-4">
            팀 동료 정성 분석 기반 — 정량 데이터 연동 진행 중
          </p>
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="border-b border-[var(--color-border)]">
                <th className="text-left py-2.5 text-[var(--color-text-muted)]">키워드</th>
                <th className="text-center py-2.5 text-[var(--color-text-muted)]">런웨이</th>
                <th className="text-center py-2.5 text-[var(--color-text-muted)]">검증 상태</th>
                <th className="text-left py-2.5 text-[var(--color-text-muted)] w-48">전파 진행도</th>
              </tr>
            </thead>
            <tbody>
              {SAMPLE_KEYWORDS.map((kw) => (
                <tr key={kw.keyword} className="border-b border-[var(--color-border)]/50 hover:bg-gray-50">
                  <td className="py-2.5 font-medium text-[var(--color-text)]">{kw.keyword}</td>
                  <td className="py-2.5 text-center text-[var(--color-text-secondary)]">{kw.runway}</td>
                  <td className="py-2.5 text-center">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                      kw.status.includes("확인") ? "bg-emerald-100 text-emerald-700" :
                      kw.status.includes("검증") ? "bg-blue-100 text-blue-700" :
                      "bg-gray-100 text-gray-500"
                    }`}>
                      {kw.status}
                    </span>
                  </td>
                  <td className="py-2.5">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${kw.propagation}%`,
                            backgroundColor: kw.propagation > 70 ? "#059669" : kw.propagation > 50 ? "#3266ad" : "#9CA3AF",
                          }}
                        />
                      </div>
                      <span className="text-[10px] text-[var(--color-text-muted)] w-8 text-right">{kw.propagation}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="text-center text-[11px] text-[var(--color-text-muted)] mt-6 py-4">
          기타 Origin 타입 (Capital-driven, Viral/Meme, Market-organic)은{" "}
          <a href="/archive/flow" className="underline hover:text-[var(--color-primary)]">Archive</a>에서 확인
        </div>
      </div>
    </main>
  );
}
