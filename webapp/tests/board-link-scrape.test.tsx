import { describe, it } from "vitest";

/**
 * Wave 0 stubs: BoardCard link scrape UI contracts (D-06, D-20, D-22, D-29).
 * Implemented in plans 05.2-01/02/03.
 */
describe("BoardCard link scrape states", () => {
  it.todo("uses item.image for thumbnail src when scrape_status is ok (D-06)");

  it.todo(
    "shows spinner affordance when scrape_status is pending or scraping (D-22)",
  );

  it.todo("never renders raw scrape_status code string in the DOM (D-20)");

  it.todo(
    "OG preview uses native img with referrerPolicy no-referrer (D-29)",
  );
});
