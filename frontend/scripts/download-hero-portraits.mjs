/**
 * One-time download of hero portrait thumbnails from the MLBB Fandom wiki
 * (MediaWiki pageimages API) into public/assets/heroes/{slug}.webp, where
 * slug matches src/lib/roleColors.ts's heroSlug() so HeroAvatar resolves
 * them automatically. The Fandom CDN serves thumbnails as WebP regardless
 * of the source file's original format, so files are saved as .webp rather
 * than mislabeling them .png. Re-run any time the hero roster changes;
 * existing files are skipped unless --force is passed.
 *
 * Usage: node scripts/download-hero-portraits.mjs [--force]
 */
import { mkdir, writeFile, access } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const API_BASE_URL = process.env.API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
const WIKI_API = "https://mobile-legends.fandom.com/api.php";
const OUT_DIR = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "public", "assets", "heroes");
const FORCE = process.argv.includes("--force");
const REQUEST_DELAY_MS = 350;

function heroSlug(name) {
  return name
    .toLowerCase()
    .replace(/[.'%]/g, "")
    .replace(/\s+/g, "-");
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fileExists(filePath) {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function fetchHeroes() {
  const res = await fetch(`${API_BASE_URL}/heroes`);
  if (!res.ok) throw new Error(`Failed to fetch hero list: ${res.status}`);
  return res.json();
}

async function fetchThumbnailUrl(heroName) {
  const url = new URL(WIKI_API);
  url.search = new URLSearchParams({
    action: "query",
    titles: heroName,
    prop: "pageimages",
    pithumbsize: "400",
    redirects: "1",
    format: "json",
  }).toString();

  const res = await fetch(url);
  if (!res.ok) throw new Error(`Wiki API HTTP ${res.status}`);
  const data = await res.json();
  const pages = data?.query?.pages ?? {};
  const page = Object.values(pages)[0];
  return page?.thumbnail?.source ?? null;
}

async function downloadImage(url, destPath) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Image HTTP ${res.status}`);
  const buffer = Buffer.from(await res.arrayBuffer());
  await writeFile(destPath, buffer);
}

async function main() {
  await mkdir(OUT_DIR, { recursive: true });

  const heroes = await fetchHeroes();
  console.log(`Fetched ${heroes.length} heroes from ${API_BASE_URL}/heroes`);

  const missing = [];
  const skipped = [];
  const downloaded = [];

  for (const hero of heroes) {
    const slug = heroSlug(hero.name);
    const destPath = path.join(OUT_DIR, `${slug}.webp`);

    if (!FORCE && (await fileExists(destPath))) {
      skipped.push(hero.name);
      continue;
    }

    try {
      const thumbUrl = await fetchThumbnailUrl(hero.name);
      if (!thumbUrl) {
        console.warn(`  ! No thumbnail found for "${hero.name}"`);
        missing.push(hero.name);
        continue;
      }
      await downloadImage(thumbUrl, destPath);
      console.log(`  + ${hero.name} -> assets/heroes/${slug}.webp`);
      downloaded.push(hero.name);
    } catch (err) {
      console.warn(`  ! Failed for "${hero.name}": ${err.message}`);
      missing.push(hero.name);
    }

    await sleep(REQUEST_DELAY_MS);
  }

  console.log("\nSummary:");
  console.log(`  Downloaded: ${downloaded.length}`);
  console.log(`  Skipped (already present): ${skipped.length}`);
  console.log(`  Missing/failed: ${missing.length}${missing.length ? ` (${missing.join(", ")})` : ""}`);
  console.log("\nHeroes without a downloaded portrait fall back to the role-colored initials avatar automatically.");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
