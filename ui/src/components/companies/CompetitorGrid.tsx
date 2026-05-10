import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Competitor } from "@/lib/types";

export function CompetitorGrid({ competitors }: { competitors: Competitor[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {competitors.map((c, i) => (
        <Card key={i}>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">{c.name}</CardTitle>
              <span className="font-mono text-sm">{c.strength_score}/100</span>
            </div>
            <div className="h-1.5 rounded-full bg-muted overflow-hidden">
              <div
                className="h-full bg-primary"
                style={{ width: `${c.strength_score}%` }}
              />
            </div>
          </CardHeader>
          <CardContent>
            <ul className="list-disc pl-5 space-y-1 text-sm">
              {c.summary.map((s, j) => (
                <li key={j}>{s}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
