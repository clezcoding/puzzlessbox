export type EmptyCopy = {
  heading: string;
  body: string;
  image: string;
};

const EMPTY_BY_NAME: Record<string, EmptyCopy> = {
  Inbox: {
    heading: "Hier ist gähnende Leere.",
    body: "Apollo hat noch nichts gefangen. Sende eine Nachricht, um den ersten Eintrag zu stashen.",
    image: "/apollo-empty-inbox.png",
  },
  Notizen: {
    heading: "Hier ist gähnende Leere.",
    body: "Keine Notizen stasht sich von selbst. Lass Apollo etwas aufschreiben.",
    image: "/apollo-empty-notes.png",
  },
  Links: {
    heading: "Hier ist gähnende Leere.",
    body: "Noch keine Links gestasht. Apollo sammelt sie gern ein.",
    image: "/apollo-empty-links.png",
  },
  Tasks: {
    heading: "Hier ist gähnende Leere.",
    body: "Keine Tasks in Sicht. Apollo wartet auf deinen nächsten Auftrag.",
    image: "/apollo-empty-tasks.png",
  },
  Termine: {
    heading: "Hier ist gähnende Leere.",
    body: "Kein Termin in Sicht. Apollo hält den Kalender bereit.",
    image: "/apollo-empty-cal.png",
  },
};

export function getEmptyCopy(categoryName: string): EmptyCopy {
  return (
    EMPTY_BY_NAME[categoryName] ?? {
      heading: "Hier ist gähnende Leere.",
      body: "Apollo hat noch nichts gefangen.",
      image: "/apollo-empty-inbox.png",
    }
  );
}
