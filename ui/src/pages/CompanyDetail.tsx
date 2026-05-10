import { useParams, Link } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Companies } from "@/lib/api";
import { ScoreGauge } from "@/components/companies/ScoreGauge";
import { CompetitorGrid } from "@/components/companies/CompetitorGrid";
import { BulletList } from "@/components/companies/BulletList";
import { InvestmentMemo } from "@/components/companies/InvestmentMemo";
import { NotesPanel } from "@/components/companies/NotesPanel";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Star, RefreshCw, Download, ArrowLeft } from "lucide-react";
import { toast } from "sonner";

export default function CompanyDetail() {
  const { id = "" } = useParams();
  const qc = useQueryClient();
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["company", id],
    queryFn: () => Companies.get(id),
    enabled: !!id,
  });

  if (isLoading || !data) {
    return <div className="text-muted-foreground">Loading…</div>;
  }

  const regen = async () => {
    if (!confirm("Regenerate the AI report? Existing competitors will be replaced.")) return;
    try {
      await Companies.regenerate(id);
      await refetch();
      toast.success("Report regenerated");
    } catch (e: unknown) {
      const detail =
        (e as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        "Failed to regenerate";
      toast.error(detail);
    }
  };

  const fav = async () => {
    await Companies.patch(id, { favorite: !data.favorite });
    refetch();
    qc.invalidateQueries({ queryKey: ["companies"] });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <Link to="/" className="text-sm text-muted-foreground inline-flex items-center gap-1">
            <ArrowLeft className="h-3 w-3" /> Back
          </Link>
          <div className="flex items-center gap-3 mt-1">
            <h1 className="text-2xl font-semibold tracking-tight">{data.name}</h1>
            <button onClick={fav} aria-label="favorite">
              <Star
                className={
                  data.favorite
                    ? "h-5 w-5 fill-yellow-400 text-yellow-500"
                    : "h-5 w-5 text-muted-foreground"
                }
              />
            </button>
            {data.market_tag && <Badge variant="secondary">{data.market_tag}</Badge>}
          </div>
          <div className="text-sm text-muted-foreground mt-1">
            {data.hq || "—"} ·{" "}
            {data.website ? (
              <a className="underline" href={data.website} target="_blank" rel="noreferrer">
                {data.website}
              </a>
            ) : (
              "—"
            )}{" "}
            · created {new Date(data.created_at).toLocaleDateString()}
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={regen}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Regenerate
          </Button>
          <a href={Companies.exportUrl(id)} target="_blank" rel="noreferrer">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export PDF
            </Button>
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-1">
          <ScoreGauge total={data.score_total} breakdown={data.score_breakdown} />
        </div>
        <div className="lg:col-span-2 border rounded-2xl bg-background p-6">
          <h3 className="font-medium mb-2">Summary</h3>
          <BulletList items={data.summary} />
        </div>
      </div>

      <Tabs defaultValue="thesis">
        <TabsList>
          <TabsTrigger value="thesis">Investment Thesis</TabsTrigger>
          <TabsTrigger value="risks">Risks</TabsTrigger>
          <TabsTrigger value="why">Why It Matters</TabsTrigger>
          <TabsTrigger value="memo">Investment Memo</TabsTrigger>
          <TabsTrigger value="competitors">Competitors</TabsTrigger>
          <TabsTrigger value="notes">Notes</TabsTrigger>
        </TabsList>
        <TabsContent value="thesis" className="border rounded-2xl bg-background p-6">
          <BulletList items={data.investment_thesis} />
        </TabsContent>
        <TabsContent value="risks" className="border rounded-2xl bg-background p-6">
          <BulletList items={data.risks} />
        </TabsContent>
        <TabsContent value="why" className="border rounded-2xl bg-background p-6">
          <BulletList items={data.why_matters} />
        </TabsContent>
        <TabsContent value="memo" className="border rounded-2xl bg-background p-6">
          <InvestmentMemo markdown={data.memo_markdown} />
        </TabsContent>
        <TabsContent value="competitors" className="border rounded-2xl bg-background p-6">
          <CompetitorGrid competitors={data.competitors} />
        </TabsContent>
        <TabsContent value="notes" className="border rounded-2xl bg-background p-6">
          <NotesPanel companyId={id} notes={data.notes} onChange={() => refetch()} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
