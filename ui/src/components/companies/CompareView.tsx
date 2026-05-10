import type { ReactNode } from "react";
import type { CompanyDetail } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { BulletList } from "./BulletList";

const Cell = ({ title, children }: { title: string; children: ReactNode }) => (
  <div className="border rounded-2xl p-5 bg-background">
    <h4 className="font-medium mb-2">{title}</h4>
    {children}
  </div>
);

const Column = ({ c }: { c: CompanyDetail }) => (
  <div className="space-y-4">
    <div className="border rounded-2xl p-5 bg-background">
      <div className="text-sm text-muted-foreground">{c.market_tag}</div>
      <h2 className="text-xl font-semibold">{c.name}</h2>
      <div className="text-3xl font-bold mt-2">
        {c.score_total ?? "—"}
        <span className="text-sm text-muted-foreground"> /100</span>
      </div>
    </div>
    <Cell title="Summary">
      <BulletList items={c.summary} />
    </Cell>
    <Cell title="Thesis">
      <BulletList items={c.investment_thesis} />
    </Cell>
    <Cell title="Risks">
      <BulletList items={c.risks} />
    </Cell>
    <Cell title="Why it matters">
      <BulletList items={c.why_matters} />
    </Cell>
    <Cell title="Top competitor">
      {c.competitors[0] ? (
        <div className="text-sm">
          <Badge variant="secondary">{c.competitors[0].name}</Badge> — strength{" "}
          {c.competitors[0].strength_score}/100
        </div>
      ) : (
        <span className="text-muted-foreground text-sm">—</span>
      )}
    </Cell>
  </div>
);

export function CompareView({ a, b }: { a: CompanyDetail; b: CompanyDetail }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Column c={a} />
      <Column c={b} />
    </div>
  );
}
