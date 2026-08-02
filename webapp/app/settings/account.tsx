"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authClient } from "@/lib/auth-client";

type AccountSectionProps = {
  email?: string | null;
};

export function AccountSection({ email }: AccountSectionProps) {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setFormError(null);
    if (!currentPassword) {
      setFormError("Aktuelles Passwort fehlt.");
      return;
    }
    if (newPassword.length < 8) {
      setFormError("Mindestens 8 Zeichen.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setFormError("Passwörter stimmen nicht überein.");
      return;
    }

    setSubmitting(true);
    try {
      await authClient.changePassword({
        currentPassword,
        newPassword,
      });
      toast.success("Passwort geändert.");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch {
      toast.error("Passwort konnte nicht geändert werden.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleLogout() {
    await authClient.signOut();
    router.push("/login");
  }

  return (
    <div className="space-y-6">
      {email ? (
        <p
          className="truncate text-sm text-muted-foreground"
          title={email}
        >
          {email}
        </p>
      ) : null}

      <form className="space-y-4" onSubmit={onSubmit}>
        {formError ? (
          <p className="text-sm text-destructive">{formError}</p>
        ) : null}
        <div className="space-y-2">
          <Label htmlFor="current-password">Aktuelles Passwort</Label>
          <Input
            id="current-password"
            type="password"
            autoComplete="current-password"
            value={currentPassword}
            onChange={(event) => setCurrentPassword(event.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="new-password">Neues Passwort</Label>
          <Input
            id="new-password"
            type="password"
            autoComplete="new-password"
            value={newPassword}
            onChange={(event) => setNewPassword(event.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="confirm-password">Passwort bestätigen</Label>
          <Input
            id="confirm-password"
            type="password"
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
          />
        </div>
        <Button type="submit" disabled={submitting}>
          Passwort ändern
        </Button>
      </form>

      <Button type="button" variant="outline" onClick={() => void handleLogout()}>
        Abmelden
      </Button>
    </div>
  );
}
