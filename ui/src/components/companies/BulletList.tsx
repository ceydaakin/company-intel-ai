export function BulletList({ items }: { items: string[] | null }) {
  if (!items?.length) return <p className="text-muted-foreground text-sm">—</p>;
  return (
    <ul className="list-disc pl-5 space-y-1.5 text-sm">
      {items.map((t, i) => (
        <li key={i}>{t}</li>
      ))}
    </ul>
  );
}
