import { useState } from "react";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Companies } from "@/lib/api";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { Loader2, Sparkles } from "lucide-react";

interface Props {
  open: boolean;
  onOpenChange: (v: boolean) => void;
}

export function CreateCompanyModal({ open, onOpenChange }: Props) {
  const [form, setForm] = useState({ name: "", hq: "", website: "", context: "" });
  const [busy, setBusy] = useState(false);
  const nav = useNavigate();
  const qc = useQueryClient();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      const payload: { name: string; hq?: string; website?: string; context?: string } = {
        name: form.name,
      };
      if (form.hq) payload.hq = form.hq;
      if (form.website) payload.website = form.website;
      if (form.context) payload.context = form.context;
      const created = await Companies.create(payload);
      qc.invalidateQueries({ queryKey: ["companies"] });
      toast.success("Report generated");
      onOpenChange(false);
      nav(`/companies/${created.id}`);
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        "Failed to create company";
      toast.error(detail);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Create company</DialogTitle>
        </DialogHeader>
        <form onSubmit={submit} className="space-y-4">
          <div className="space-y-2">
            <Label>Company name *</Label>
            <Input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label>HQ</Label>
            <Input
              value={form.hq}
              onChange={(e) => setForm({ ...form, hq: e.target.value })}
              placeholder="San Francisco, CA"
            />
          </div>
          <div className="space-y-2">
            <Label>Website</Label>
            <Input
              type="url"
              value={form.website}
              onChange={(e) => setForm({ ...form, website: e.target.value })}
              placeholder="https://acme.com"
            />
          </div>
          <div className="space-y-2">
            <Label>Context (optional)</Label>
            <Textarea
              rows={3}
              value={form.context}
              onChange={(e) => setForm({ ...form, context: e.target.value })}
              placeholder="Anything you'd like the AI to know"
            />
          </div>
          {busy && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground bg-muted rounded-lg p-3">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Researching, analyzing competitors, scoring… this takes ~10s</span>
            </div>
          )}
          <DialogFooter>
            <Button variant="ghost" type="button" onClick={() => onOpenChange(false)} disabled={busy}>
              Cancel
            </Button>
            <Button type="submit" disabled={busy}>
              <Sparkles className="h-4 w-4 mr-2" />
              {busy ? "Generating…" : "Generate report"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
