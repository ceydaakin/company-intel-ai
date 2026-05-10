import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Companies, Compare as Cmp } from "@/lib/api";
import { CompareView } from "@/components/companies/CompareView";

export default function Compare() {
  const list = useQuery({
    queryKey: ["companies", "all-for-compare"],
    queryFn: () => Companies.list({}),
  });
  const [a, setA] = useState<string>("");
  const [b, setB] = useState<string>("");

  useEffect(() => {
    if (!list.data) return;
    if (!a && list.data[0]) setA(list.data[0].id);
    if (!b && list.data[1]) setB(list.data[1].id);
  }, [list.data, a, b]);

  const result = useQuery({
    queryKey: ["compare", a, b],
    queryFn: () => Cmp.run(a, b),
    enabled: !!a && !!b && a !== b,
  });

  const opts = list.data ?? [];
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight">Compare</h1>
      <div className="flex gap-3 items-center">
        <select
          value={a}
          onChange={(e) => setA(e.target.value)}
          className="h-9 rounded-md border bg-background px-2 text-sm"
        >
          {opts.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <span className="text-muted-foreground">vs</span>
        <select
          value={b}
          onChange={(e) => setB(e.target.value)}
          className="h-9 rounded-md border bg-background px-2 text-sm"
        >
          {opts.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>
      {a === b && <p className="text-sm text-muted-foreground">Pick two different companies.</p>}
      {result.data && <CompareView a={result.data.a} b={result.data.b} />}
    </div>
  );
}
