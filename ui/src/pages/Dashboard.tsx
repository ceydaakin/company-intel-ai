import { useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Companies } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { CreateCompanyModal } from "@/components/companies/CreateCompanyModal";
import { CompanyTable } from "@/components/companies/CompanyTable";
import { CompanyFilters } from "@/components/companies/CompanyFilters";
import { EmptyState } from "@/components/companies/EmptyState";
import { Plus } from "lucide-react";
import { toast } from "sonner";

export default function Dashboard() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [marketTag, setMarketTag] = useState("");
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["companies", { q, marketTag, favoritesOnly }],
    queryFn: () =>
      Companies.list({
        q: q || undefined,
        market_tag: marketTag || undefined,
        favorite: favoritesOnly || undefined,
      }),
  });

  const marketTags = useMemo(
    () =>
      Array.from(
        new Set((data ?? []).map((c) => c.market_tag).filter(Boolean) as string[]),
      ).sort(),
    [data],
  );

  const toggleFavorite = async (id: string, value: boolean) => {
    try {
      await Companies.patch(id, { favorite: value });
      qc.invalidateQueries({ queryKey: ["companies"] });
    } catch {
      toast.error("Failed to update favorite");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Companies</h1>
          <p className="text-muted-foreground text-sm">
            AI-generated intelligence reports for VC analysis.
          </p>
        </div>
        <Button onClick={() => setOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create company
        </Button>
      </div>

      <CompanyFilters
        q={q}
        setQ={setQ}
        marketTag={marketTag}
        setMarketTag={setMarketTag}
        favoritesOnly={favoritesOnly}
        setFavoritesOnly={setFavoritesOnly}
        marketTags={marketTags}
      />

      {isLoading ? (
        <div className="text-muted-foreground text-sm">Loading…</div>
      ) : data && data.length > 0 ? (
        <CompanyTable companies={data} onToggleFavorite={toggleFavorite} />
      ) : (
        <EmptyState onCreate={() => setOpen(true)} />
      )}

      <CreateCompanyModal open={open} onOpenChange={setOpen} />
    </div>
  );
}
