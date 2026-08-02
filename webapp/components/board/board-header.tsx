"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Moon, RefreshCw, Sun } from "lucide-react";

import { authClient } from "@/lib/auth-client";
import { useTheme } from "@/lib/hooks/use-theme";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

type BoardHeaderProps = {
  userEmail?: string | null;
  onRefresh?: () => void;
};

export function BoardHeader({ userEmail, onRefresh }: BoardHeaderProps) {
  const router = useRouter();
  const { theme, toggleTheme } = useTheme();

  async function handleLogout() {
    await authClient.signOut();
    router.push("/login");
  }

  return (
    <header className="flex items-center justify-between gap-4 border-b border-border bg-background px-4 py-3">
      <div className="flex min-w-0 items-center gap-3">
        <Image
          src="/apollo-wordmark.png"
          alt="Puzzlessbox"
          width={120}
          height={32}
          className="h-8 w-auto"
          priority
        />
      </div>

      <div className="flex items-center gap-2">
        <Button
          type="button"
          variant="outline"
          size="icon"
          aria-label="Board aktualisieren"
          onClick={onRefresh}
        >
          <RefreshCw className="size-4" />
        </Button>

        <Button
          type="button"
          variant="outline"
          size="icon"
          aria-label="Darstellung umschalten"
          onClick={toggleTheme}
        >
          {theme === "dark" ? (
            <Sun className="size-4" />
          ) : (
            <Moon className="size-4" />
          )}
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              type="button"
              className="rounded-full outline-none focus-visible:ring-2 focus-visible:ring-ring"
              aria-label="Konto-Menü"
            >
              <Avatar>
                <AvatarImage src="/apollo-avatar.png" alt="" />
                <AvatarFallback>AP</AvatarFallback>
              </Avatar>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            {userEmail ? (
              <p
                className="truncate px-2 py-1.5 text-sm text-muted-foreground"
                title={userEmail}
              >
                {userEmail}
              </p>
            ) : null}
            <DropdownMenuItem asChild>
              <Link href="/settings">Einstellungen</Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout}>Abmelden</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
