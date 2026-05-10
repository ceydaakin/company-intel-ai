import type { ReactNode } from "react";
import { TopBar } from "./TopBar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-muted/30">
      <TopBar />
      <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
    </div>
  );
}
