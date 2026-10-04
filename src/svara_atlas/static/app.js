const STORAGE_KEY = "svara-atlas-library-v1";
const DEFAULT_CATEGORIES = ["Unsorted"];

const discoverButton = document.querySelector("#discover-button");
const discoverStatus = document.querySelector("#discover-status");
const importForm = document.querySelector("#import-form");
const importButton = document.querySelector("#import-button");
const playlistUrlInput = document.querySelector("#playlist-url");
const importStatus = document.querySelector("#import-status");
const categoryForm = document.querySelector("#category-form");
const categoryInput = document.querySelector("#category-name");
const songList = document.querySelector("#song-list");
const emptyState = document.querySelector("#empty-state");
const songCount = document.querySelector("#song-count");
const categoryCount = document.querySelector("#category-count");
const exportButton = document.querySelector("#export-button");

let library = loadLibrary();

function loadLibrary() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) {
      return { categories: [...DEFAULT_CATEGORIES], tracks: [] };
    }
    const parsed = JSON.parse(saved);
    if (!Array.isArray(parsed.categories) || !Array.isArray(parsed.tracks)) {
      throw new Error("Saved library has an unexpected format.");
    }
    const categories = parsed.categories.filter(
      (category) => typeof category === "string" && category.trim(),
    );
    return {
      categories: categories.length ? categories : [...DEFAULT_CATEGORIES],
      tracks: parsed.tracks.filter(
        (track) =>
          track &&
          typeof track.videoId === "string" &&
          typeof track.title === "string",
      ),
    };
  } catch (error) {
    setStatus(
      discoverStatus,
      `Could not read your saved library: ${error.message}. Clear this site's stored data to start fresh.`,
      true,
    );
    return { categories: [...DEFAULT_CATEGORIES], tracks: [] };
  }
}

function saveLibrary() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(library));
  } catch (error) {
    setStatus(discoverStatus, `Could not save your library: ${error.message}`, true);
  }
}

function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("error", isError);
}

function formatViews(value) {
  if (
    value === null ||
    value === undefined ||
    value === "" ||
    !Number.isFinite(Number(value))
  ) {
    return "view count unavailable";
  }
  return `${new Intl.NumberFormat().format(Number(value))} views`;
}

function render() {
  songList.replaceChildren();
  emptyState.hidden = library.tracks.length > 0;
  songCount.textContent = `${library.tracks.length} ${
    library.tracks.length === 1 ? "song" : "songs"
  }`;
  const categories = [...new Set(library.tracks.map((track) => track.category))];
  categoryCount.textContent = `${categories.length} ${
    categories.length === 1 ? "language list" : "language lists"
  }`;

  for (const categoryName of categories) {
    const groupTracks = library.tracks.filter(
      (track) => track.category === categoryName,
    );
    const group = document.createElement("section");
    group.className = "language-group";

    const heading = document.createElement("div");
    heading.className = "language-group-heading";
    const name = document.createElement("h3");
    name.textContent = categoryName;
    const total = document.createElement("span");
    total.textContent = `${groupTracks.length} ${
      groupTracks.length === 1 ? "result" : "results"
    }`;
    heading.append(name, total);

    const rows = document.createElement("div");
    rows.className = "song-list-group";
    for (const track of groupTracks) {
      const row = document.createElement("article");
      row.className = "song-row";

      const info = document.createElement("div");
      info.className = "song-info";

      const title = document.createElement("a");
      title.className = "song-title";
      title.href = `https://www.youtube.com/watch?v=${encodeURIComponent(track.videoId)}`;
      title.target = "_blank";
      title.rel = "noopener noreferrer";
      title.textContent = track.title;
      info.append(title);

      const details = document.createElement("span");
      details.className = "song-channel";
      details.textContent = `${track.channel || "YouTube"} · ${formatViews(track.viewCount)}`;
      info.append(details);

      const category = document.createElement("select");
      category.setAttribute("aria-label", `Category for ${track.title}`);
      for (const name of library.categories) {
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        option.selected = track.category === name;
        category.append(option);
      }
      category.addEventListener("change", () => {
        track.category = category.value;
        saveLibrary();
        render();
      });

      const remove = document.createElement("button");
      remove.className = "remove-song";
      remove.type = "button";
      remove.setAttribute("aria-label", `Remove ${track.title}`);
      remove.textContent = "×";
      remove.addEventListener("click", () => {
        library.tracks = library.tracks.filter(
          (candidate) => candidate.videoId !== track.videoId,
        );
        saveLibrary();
        render();
      });

      row.append(info, category, remove);
      rows.append(row);
    }
    group.append(heading, rows);
    songList.append(group);
  }
  saveLibrary();
}

discoverButton.addEventListener("click", async () => {
  discoverButton.disabled = true;
  discoverButton.textContent = "Finding popular songs…";
  setStatus(discoverStatus, "Searching YouTube and checking view counts…");

  try {
    const response = await fetch("/api/discover");
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "Automatic discovery failed.");
    }

    const previousTracks = library.tracks.filter((track) => !track.automatic);
    const seenIds = new Set(previousTracks.map((track) => track.videoId));
    const automaticTracks = [];
    for (const language of result.languages) {
      for (const track of result.songsByLanguage[language] || []) {
        if (!seenIds.has(track.videoId)) {
          seenIds.add(track.videoId);
          automaticTracks.push(track);
        }
      }
    }

    library.tracks = [...previousTracks, ...automaticTracks];
    const previousCategories = library.categories.filter(
      (category) => category !== "Unsorted",
    );
    previousCategories.push(
      ...previousTracks.map((track) => track.category).filter(Boolean),
    );
    library.categories = [
      ...new Set([...previousCategories, ...result.languages]),
    ];
    render();

    const counts = result.languages
      .map((language) => {
        const count = (result.songsByLanguage[language] || []).length;
        return `${language}: ${count}`;
      })
      .join(" · ");
    setStatus(
      discoverStatus,
      `Updated estimated lists (${counts}). YouTube search results can include duplicates or miscategorized videos.`,
    );
  } catch (error) {
    setStatus(discoverStatus, error.message, true);
  } finally {
    discoverButton.disabled = false;
    discoverButton.innerHTML = 'Generate my lists <span aria-hidden="true">↗</span>';
  }
});

categoryForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const category = categoryInput.value.trim();
  if (!category) {
    setStatus(discoverStatus, "Enter a name for your category.", true);
    return;
  }
  if (
    library.categories.some(
      (existing) => existing.toLocaleLowerCase() === category.toLocaleLowerCase(),
    )
  ) {
    setStatus(discoverStatus, "That category already exists.", true);
    return;
  }
  library.categories.push(category);
  categoryInput.value = "";
  setStatus(discoverStatus, `Added category “${category}”.`);
  render();
});

importForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  importButton.disabled = true;
  importButton.textContent = "Importing…";
  setStatus(importStatus, "Fetching playlist details from YouTube…");

  try {
    const response = await fetch(
      `/api/playlist?${new URLSearchParams({ url: playlistUrlInput.value })}`,
    );
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "Playlist import failed.");
    }

    const knownIds = new Set(library.tracks.map((track) => track.videoId));
    const newTracks = result.tracks.filter((track) => !knownIds.has(track.videoId));
    library.tracks.push(
      ...newTracks.map((track) => ({
        ...track,
        category: "Unsorted",
        viewCount: null,
        automatic: false,
      })),
    );
    if (newTracks.length && !library.categories.includes("Unsorted")) {
      library.categories.push("Unsorted");
    }
    render();
    setStatus(
      importStatus,
      newTracks.length
        ? `Added ${newTracks.length} song${newTracks.length === 1 ? "" : "s"}.`
        : "No new songs found; this playlist is already in your library.",
    );
    playlistUrlInput.value = "";
  } catch (error) {
    setStatus(importStatus, error.message, true);
  } finally {
    importButton.disabled = false;
    importButton.innerHTML = 'Import songs <span aria-hidden="true">↗</span>';
  }
});

function csvCell(value) {
  return `"${String(value).replaceAll('"', '""')}"`;
}

exportButton.addEventListener("click", () => {
  if (!library.tracks.length) {
    setStatus(discoverStatus, "Generate lists before exporting your song list.", true);
    return;
  }
  const rows = [["Title", "Language list", "Channel", "YouTube views", "YouTube URL"]];
  for (const category of library.categories) {
    for (const track of library.tracks.filter((song) => song.category === category)) {
      rows.push([
        track.title,
        category,
        track.channel || "",
        track.viewCount ?? "",
        `https://www.youtube.com/watch?v=${track.videoId}`,
      ]);
    }
  }
  const csv = rows.map((row) => row.map(csvCell).join(",")).join("\r\n");
  const blob = new Blob([`\ufeff${csv}`], { type: "text/csv;charset=utf-8" });
  const downloadUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = downloadUrl;
  link.download = "svara-atlas-popular-songs.csv";
  link.click();
  URL.revokeObjectURL(downloadUrl);
  setStatus(discoverStatus, "Downloaded your estimated language lists.");
});

render();
