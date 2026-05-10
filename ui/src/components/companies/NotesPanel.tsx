import { useState } from "react";
import { Notes } from "@/lib/api";
import type { Note } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Trash2 } from "lucide-react";

interface Props {
  companyId: string;
  notes: Note[];
  onChange: () => void;
}

export function NotesPanel({ companyId, notes, onChange }: Props) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);

  const add = async () => {
    if (!text.trim()) return;
    setBusy(true);
    await Notes.add(companyId, text.trim());
    setText("");
    setBusy(false);
    onChange();
  };

  const remove = async (id: string) => {
    await Notes.remove(companyId, id);
    onChange();
  };

  return (
    <div className="space-y-3">
      <Textarea
        rows={3}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Add a note…"
      />
      <Button size="sm" onClick={add} disabled={busy || !text.trim()}>
        Add note
      </Button>
      <ul className="space-y-2">
        {notes.map((n) => (
          <li
            key={n.id}
            className="border rounded-lg p-3 text-sm bg-background flex items-start gap-2"
          >
            <span className="flex-1 whitespace-pre-wrap">{n.body}</span>
            <Button variant="ghost" size="icon" onClick={() => remove(n.id)}>
              <Trash2 className="h-4 w-4" />
            </Button>
          </li>
        ))}
        {notes.length === 0 && (
          <li className="text-muted-foreground text-sm">No notes yet.</li>
        )}
      </ul>
    </div>
  );
}
