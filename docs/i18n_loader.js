const I18N_PATHS = (() => {
  const scriptUrl = document.currentScript
    ? new URL(document.currentScript.src)
    : new URL(window.location.href);
  const scriptDir = new URL("./", scriptUrl);
  const pageDir = new URL("./", window.location.href);
  const candidates = [
    new URL("startups_i18n.json", scriptDir).href,
    new URL("startups_i18n.json", pageDir).href,
    new URL("../src/startups/locales/startups_i18n.json", scriptDir).href,
    new URL("../src/startups/locales/startups_i18n.json", pageDir).href,
  ];
  return candidates.filter((value, index, all) => all.indexOf(value) === index);
})();

async function loadStartupsI18nBundle() {
  if (window.startupsI18nBundle) return window.startupsI18nBundle;
  if (window.__startupsI18nPromise) return window.__startupsI18nPromise;
  const loadTask = (async () => {
    for (const path of I18N_PATHS) {
      try {
        const response = await fetch(path, { cache: "no-store" });
        if (!response.ok) continue;
        const data = await response.json();
        window.startupsI18nBundle = data;
        return data;
      } catch (error) {
        // Continue trying alternative paths.
        continue;
      }
    }
    throw new Error("Failed to load startups_i18n.json.");
  })();
  window.__startupsI18nPromise = loadTask;
  return loadTask;
}

window.loadStartupsI18nBundle = loadStartupsI18nBundle;
