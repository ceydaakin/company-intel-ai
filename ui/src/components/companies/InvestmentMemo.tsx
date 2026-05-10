import ReactMarkdown from "react-markdown";

export function InvestmentMemo({ markdown }: { markdown: string | null }) {
  if (!markdown) {
    return <p className="text-muted-foreground text-sm">No memo generated.</p>;
  }
  return (
    <article className="prose prose-sm max-w-none">
      <ReactMarkdown>{markdown}</ReactMarkdown>
    </article>
  );
}
