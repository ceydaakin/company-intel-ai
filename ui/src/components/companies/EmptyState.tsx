import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";

export function EmptyState({ onCreate }: { onCreate: () => void }) {
  return (
    <div className="border border-dashed rounded-2xl p-16 text-center bg-background">
      <Sparkles className="mx-auto mb-3 h-8 w-8 text-muted-foreground" />
      <h3 className="font-medium">No companies yet</h3>
      <p className="text-sm text-muted-foreground mb-4">
        Create your first AI-generated company report.
      </p>
      <Button onClick={onCreate}>Create company</Button>
    </div>
  );
}
