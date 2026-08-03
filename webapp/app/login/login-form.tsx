"use client";

import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { authClient } from "@/lib/auth-client";
import { getSafeNextPath } from "@/lib/redirect";

const SIGNUP_LOCKED_COPY =
  "Registrierung ist geschlossen. Apollo lässt nur den ersten Nutzer rein.";
const SIGNUP_LOCKED_STORAGE_KEY = "pb.signup_locked";

function readSignupLockedFlag(): boolean {
  if (typeof window === "undefined") return false;
  return sessionStorage.getItem(SIGNUP_LOCKED_STORAGE_KEY) === "1";
}

function isSignupLockedError(error: unknown): boolean {
  if (!error || typeof error !== "object") return false;
  const err = error as { message?: string; code?: string };
  return (
    err.message === "SIGNUP_LOCKED" ||
    err.code === "SIGNUP_LOCKED" ||
    (typeof err.message === "string" && err.message.includes("SIGNUP_LOCKED")) ||
    JSON.stringify(error).includes("SIGNUP_LOCKED")
  );
}

function lockSignupUi(
  setSignupLocked: (v: boolean) => void,
  setActiveTab: (v: "login" | "register") => void,
) {
  sessionStorage.setItem(SIGNUP_LOCKED_STORAGE_KEY, "1");
  setSignupLocked(true);
  setActiveTab("register");
}

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = getSafeNextPath(searchParams.get("next"));

  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [registerEmail, setRegisterEmail] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);
  const [registerLoading, setRegisterLoading] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);
  const [registerError, setRegisterError] = useState<string | null>(null);
  // Sticky across remounts — Better Auth returns { error } (no throw); prior
  // code pushed "/" on 409 and wiped the VOICE copy on the next remount.
  const [signupLocked, setSignupLocked] = useState(readSignupLockedFlag);
  const [activeTab, setActiveTab] = useState<"login" | "register">(() =>
    readSignupLockedFlag() ? "register" : "login",
  );

  useEffect(() => {
    if (readSignupLockedFlag()) {
      setSignupLocked(true);
      setActiveTab("register");
    }
  }, []);

  function handleTabChange(value: string) {
    const tab = value as "login" | "register";
    setActiveTab(tab);
    if (tab === "login") {
      sessionStorage.removeItem(SIGNUP_LOCKED_STORAGE_KEY);
      setSignupLocked(false);
    }
  }

  async function handleLogin(event: React.FormEvent) {
    event.preventDefault();
    setLoginLoading(true);
    setLoginError(null);
    try {
      // Better Auth client returns { data, error } — does not throw on 4xx.
      const { error } = await authClient.signIn.email({
        email: loginEmail,
        password: loginPassword,
      });
      if (error) {
        setLoginError("Anmeldung fehlgeschlagen.");
        return;
      }
      // "/" → HomeRedirect picks /welcome (first login) or /board (D-31)
      router.push(nextPath ?? "/");
    } catch {
      setLoginError("Anmeldung fehlgeschlagen.");
    } finally {
      setLoginLoading(false);
    }
  }

  async function handleRegister(event: React.FormEvent) {
    event.preventDefault();
    setRegisterLoading(true);
    setRegisterError(null);
    try {
      const { error } = await authClient.signUp.email({
        email: registerEmail,
        password: registerPassword,
        name: registerEmail.split("@")[0] ?? "Nutzer",
      });
      if (error) {
        if (isSignupLockedError(error)) {
          lockSignupUi(setSignupLocked, setActiveTab);
        } else {
          setRegisterError("Registrierung fehlgeschlagen.");
        }
        return;
      }
      sessionStorage.removeItem(SIGNUP_LOCKED_STORAGE_KEY);
      router.push(nextPath ?? "/");
    } catch (error) {
      if (isSignupLockedError(error)) {
        lockSignupUi(setSignupLocked, setActiveTab);
      } else {
        setRegisterError("Registrierung fehlgeschlagen.");
      }
    } finally {
      setRegisterLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center bg-bg-wash px-4 py-10">
      <div className="mb-8 flex flex-col items-center gap-3 text-center">
        <Image
          src="/apollo-splash.png"
          alt=""
          width={160}
          height={160}
          className="h-32 w-32"
          priority
        />
        <h1 className="font-[family-name:var(--font-display)] text-3xl text-foreground">
          Puzzlessbox
        </h1>
      </div>

      <div className="w-full max-w-md rounded-lg border border-border bg-card p-6 shadow-sm">
        <Tabs value={activeTab} onValueChange={handleTabChange}>
          <TabsList className="mb-6 grid w-full grid-cols-2">
            <TabsTrigger value="login">Anmelden</TabsTrigger>
            <TabsTrigger value="register">Registrieren</TabsTrigger>
          </TabsList>

          <TabsContent value="login" forceMount>
            <form className="space-y-4" onSubmit={handleLogin}>
              <div className="space-y-2">
                <Label htmlFor="login-email">E-Mail</Label>
                <Input
                  id="login-email"
                  type="email"
                  autoComplete="email"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="login-password">Passwort</Label>
                <Input
                  id="login-password"
                  type="password"
                  autoComplete="current-password"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  required
                />
              </div>
              {loginError ? (
                <p className="text-sm text-destructive">{loginError}</p>
              ) : null}
              <Button type="submit" className="w-full" disabled={loginLoading}>
                {loginLoading ? "Einen Moment…" : "Anmelden"}
              </Button>
            </form>
          </TabsContent>

          <TabsContent value="register" forceMount>
            <form className="space-y-4" onSubmit={handleRegister}>
              <div className="space-y-2">
                <Label htmlFor="register-email">E-Mail</Label>
                <Input
                  id="register-email"
                  type="email"
                  autoComplete="email"
                  value={registerEmail}
                  onChange={(e) => setRegisterEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="register-password">Passwort</Label>
                <Input
                  id="register-password"
                  type="password"
                  autoComplete="new-password"
                  value={registerPassword}
                  onChange={(e) => setRegisterPassword(e.target.value)}
                  required
                />
              </div>
              {signupLocked ? (
                <p className="text-sm text-muted-foreground">{SIGNUP_LOCKED_COPY}</p>
              ) : null}
              {registerError ? (
                <p className="text-sm text-destructive">{registerError}</p>
              ) : null}
              <Button type="submit" className="w-full" disabled={registerLoading}>
                {registerLoading ? "Einen Moment…" : "Konto anlegen"}
              </Button>
            </form>
          </TabsContent>
        </Tabs>
      </div>
    </main>
  );
}
