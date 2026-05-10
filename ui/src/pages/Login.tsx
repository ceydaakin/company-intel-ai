import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/lib/auth";
import { toast } from "sonner";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [u, setU] = useState("admin");
  const [p, setP] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      await login(u, p);
      nav("/");
    } catch {
      toast.error("Invalid credentials");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen grid place-items-center bg-muted">
      <form
        onSubmit={submit}
        className="bg-background border rounded-2xl shadow-sm p-8 w-[380px] space-y-4"
      >
        <div>
          <h1 className="text-xl font-semibold">Company Intel AI</h1>
          <p className="text-sm text-muted-foreground">
            Internal VC analyst tool · sign in to continue
          </p>
        </div>
        <div className="space-y-2">
          <Label>Username</Label>
          <Input value={u} onChange={(e) => setU(e.target.value)} autoFocus />
        </div>
        <div className="space-y-2">
          <Label>Password</Label>
          <Input type="password" value={p} onChange={(e) => setP(e.target.value)} />
        </div>
        <Button type="submit" disabled={busy} className="w-full">
          {busy ? "Signing in…" : "Sign in"}
        </Button>
      </form>
    </div>
  );
}
