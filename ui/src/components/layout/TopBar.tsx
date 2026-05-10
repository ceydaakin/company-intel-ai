import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth";

export function TopBar() {
  const { user, logout } = useAuth();
  const loc = useLocation();
  return (
    <header className="border-b bg-background sticky top-0 z-10">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 h-14">
        <Link to="/" className="font-semibold">
          Company Intel AI
        </Link>
        <nav className="flex items-center gap-3 text-sm">
          <Link to="/" className={loc.pathname === "/" ? "font-medium" : "text-muted-foreground"}>
            Dashboard
          </Link>
          <Link
            to="/compare"
            className={loc.pathname.startsWith("/compare") ? "font-medium" : "text-muted-foreground"}
          >
            Compare
          </Link>
          <span className="text-muted-foreground">·</span>
          <span className="text-muted-foreground">{user}</span>
          <Button variant="ghost" size="sm" onClick={logout}>
            Sign out
          </Button>
        </nav>
      </div>
    </header>
  );
}
