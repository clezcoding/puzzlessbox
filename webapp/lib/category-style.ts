const ACCENT_BY_NAME: Record<string, string> = {
  Inbox: "var(--color-inbox-accent)",
  Notizen: "var(--color-notes-accent)",
  Links: "var(--color-links-accent)",
  Tasks: "var(--color-tasks-accent)",
  Termine: "var(--color-termine-accent)",
};

const BG_BY_NAME: Record<string, string> = {
  Inbox: "var(--color-inbox-bg)",
  Notizen: "var(--color-notes-bg)",
  Links: "var(--color-links-bg)",
  Tasks: "var(--color-tasks-bg)",
  Termine: "var(--color-termine-bg)",
};

export function getCategoryAccent(categoryName: string): string {
  return ACCENT_BY_NAME[categoryName] ?? "var(--color-border-strong)";
}

export function getCategoryBg(categoryName: string): string {
  return BG_BY_NAME[categoryName] ?? "var(--color-surface-soft)";
}
