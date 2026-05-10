import { Input } from "@/components/ui/input";
import { Toggle } from "@/components/ui/toggle";
import { Star } from "lucide-react";

interface Props {
  q: string;
  setQ: (v: string) => void;
  marketTag: string;
  setMarketTag: (v: string) => void;
  favoritesOnly: boolean;
  setFavoritesOnly: (v: boolean) => void;
  marketTags: string[];
}

export function CompanyFilters(p: Props) {
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <Input
        placeholder="Search by name or website…"
        value={p.q}
        onChange={(e) => p.setQ(e.target.value)}
        className="max-w-xs"
      />
      <select
        className="h-9 rounded-md border bg-background px-2 text-sm"
        value={p.marketTag}
        onChange={(e) => p.setMarketTag(e.target.value)}
      >
        <option value="">All markets</option>
        {p.marketTags.map((t) => (
          <option key={t} value={t}>
            {t}
          </option>
        ))}
      </select>
      <Toggle pressed={p.favoritesOnly} onPressedChange={p.setFavoritesOnly}>
        <Star className="h-4 w-4 mr-1" /> Favorites
      </Toggle>
    </div>
  );
}
