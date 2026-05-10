import { Link } from "react-router-dom";
import type { CompanyListItem } from "@/lib/types";
import { Star } from "lucide-react";
import { StatusPill } from "./StatusPill";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Props {
  companies: CompanyListItem[];
  onToggleFavorite: (id: string, value: boolean) => void;
}

export function CompanyTable({ companies, onToggleFavorite }: Props) {
  return (
    <div className="border rounded-2xl overflow-hidden bg-background">
      <table className="w-full text-sm">
        <thead className="bg-muted/50">
          <tr className="text-left">
            <th className="px-4 py-3 w-10"></th>
            <th className="px-4 py-3">Company</th>
            <th className="px-4 py-3">Market</th>
            <th className="px-4 py-3">HQ</th>
            <th className="px-4 py-3">Score</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Created</th>
            <th className="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          {companies.map((c) => (
            <tr key={c.id} className="border-t hover:bg-muted/30">
              <td className="px-4 py-3">
                <button
                  onClick={() => onToggleFavorite(c.id, !c.favorite)}
                  aria-label="favorite"
                >
                  <Star
                    className={
                      c.favorite
                        ? "h-4 w-4 fill-yellow-400 text-yellow-500"
                        : "h-4 w-4 text-muted-foreground"
                    }
                  />
                </button>
              </td>
              <td className="px-4 py-3 font-medium">{c.name}</td>
              <td className="px-4 py-3">
                {c.market_tag ? <Badge variant="secondary">{c.market_tag}</Badge> : "—"}
              </td>
              <td className="px-4 py-3 text-muted-foreground">{c.hq || "—"}</td>
              <td className="px-4 py-3 font-mono">{c.score_total ?? "—"}</td>
              <td className="px-4 py-3">
                <StatusPill status={c.status} />
              </td>
              <td className="px-4 py-3 text-muted-foreground">
                {new Date(c.created_at).toLocaleDateString()}
              </td>
              <td className="px-4 py-3 text-right">
                <Button asChild size="sm" variant="ghost">
                  <Link to={`/companies/${c.id}`}>Open</Link>
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
