import type { ScoreBreakdown } from "@/lib/types";

const labels: Array<[keyof ScoreBreakdown, string]> = [
  ["market", "Market"],
  ["team", "Team"],
  ["moat", "Moat"],
  ["traction", "Traction"],
  ["fund_fit", "Fund fit"],
];

export function ScoreGauge({
  total,
  breakdown,
}: {
  total: number | null;
  breakdown: ScoreBreakdown | null;
}) {
  const score = total ?? 0;
  const tone =
    score >= 75
      ? "text-emerald-600"
      : score >= 50
        ? "text-amber-600"
        : "text-red-600";
  return (
    <div className="border rounded-2xl p-6 bg-background">
      <div className="flex items-baseline gap-3">
        <div className={`text-5xl font-bold ${tone}`}>{score}</div>
        <div className="text-muted-foreground">/ 100 deal score</div>
      </div>
      {breakdown && (
        <div className="mt-4 space-y-2">
          {labels.map(([k, label]) => (
            <div key={k}>
              <div className="flex justify-between text-xs mb-1">
                <span>{label}</span>
                <span className="font-mono">{breakdown[k]}</span>
              </div>
              <div className="h-2 rounded-full bg-muted overflow-hidden">
                <div
                  className="h-full bg-primary"
                  style={{ width: `${breakdown[k]}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
