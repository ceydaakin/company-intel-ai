import { cn } from "@/lib/cn";
import type { CompanyStatus } from "@/lib/types";

const map: Record<CompanyStatus, string> = {
  generating: "bg-yellow-100 text-yellow-800",
  ready: "bg-emerald-100 text-emerald-800",
  failed: "bg-red-100 text-red-800",
};

export function StatusPill({ status }: { status: CompanyStatus }) {
  return (
    <span className={cn("text-xs px-2 py-0.5 rounded-full font-medium", map[status])}>
      {status}
    </span>
  );
}
