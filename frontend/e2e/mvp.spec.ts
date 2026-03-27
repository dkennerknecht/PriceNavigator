import { expect, test } from "@playwright/test";

test("captures a product, creates a list and runs optimization", async ({ page }) => {
  const listName = `E2E List ${Date.now()}`;

  await page.goto("/products/new");
  await page.getByPlaceholder("https://catalog.mock/...").fill("https://catalog.mock/toolhub/milwaukee-m18fdd3-0");
  await page.getByRole("button", { name: "Produktdaten auflösen" }).click();
  await expect(page.getByLabel("Titel")).toHaveValue("Milwaukee M18 FUEL Drill Driver");
  await page.getByRole("button", { name: "Produkt speichern" }).click();
  await expect(page.getByText("Stammdaten")).toBeVisible();
  await page.getByRole("button", { name: "Mock-Angebote suchen" }).click();

  await page.goto("/shopping-lists");
  await page.getByLabel("Name").fill(listName);
  await page.getByLabel("Beschreibung").fill("Created by Playwright");
  await page.getByRole("button", { name: "Liste anlegen" }).click();
  await page.getByRole("link", { name: "Öffnen" }).first().click();

  await page.getByLabel("Produkt").selectOption({ label: "Milwaukee M18 FUEL Drill Driver" });
  await page.getByLabel("Menge").fill("1");
  await page.getByRole("button", { name: "Item hinzufügen" }).click();
  await expect(page.locator("table")).toContainText("Milwaukee M18 FUEL Drill Driver");
  await page.getByRole("button", { name: "Optimierung starten" }).click();

  await expect(page.getByText("Gesamtscore")).toBeVisible();
  await expect(page.getByRole("heading", { name: "ElectroMax" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Angebotslink" })).toBeVisible();
});
