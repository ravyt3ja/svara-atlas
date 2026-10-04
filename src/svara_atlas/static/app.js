const STORAGE_KEY = "svara-atlas-library-v1";
const DEFAULT_CATEGORIES = ["Unsorted"];

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
  const saved = localStorage.getItem(STORAGE_KEY);
  if (!saved) {
    return { categories: [...DEFAULT_CATEGORIES], tracks: [] };
  }

  try {
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
    setStatus(`Could not save your library in this browser: ${error.message}`, true);
  }
}

function setStatus(message, isError = false) {
  importStatus.textContent = message;
  importStatus.classList.toggle("error", isError);
}

function render() {
  songList.replaceChildren();
  emptyState.hidden = library.tracks.length > 0;
  songCount.textContent = `${library.tracks.length} ${
    library.tracks.length === 1 ? "song" : "songs"
  }`;
  categoryCount.textContent = `${library.categories.length} ${
    library.categories.length === 1 ? "category" : "categories"
  }`;

  for (const track of library.tracks) {
    if (!library.categories.includes(track.category)) {
      track.category = library.categories[0];
    }

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

    const channel = document.createElement("span");
    channel.className = "song-channel";
    channel.textContent = track.channel || "YouTube";
    info.append(channel);

    const category = document.createElement("select");
    category.setAttribute("aria-label", `Category for ${track.title}`);
    for (const categoryName of library.categories) {
      const option = document.createElement("option");
      option.value = categoryName;
      option.textContent = categoryName;
      option.selected = track.category === categoryName;
      category.append(option);
    }
    category.addEventListener("change", () => {
      track.category = category.value;
      saveLibrary();
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
    songList.append(row);
  }
  saveLibrary();
}

importForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  importButton.disabled = true;
  importButton.textContent = "Importing…";
  setStatus("Fetching playlist details from YouTube…");

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
      ...newTracks.map((track) => ({ ...track, category: library.categories[0] })),
    );
    render();
    setStatus(
      newTracks.length
        ? `Added ${newTracks.length} song${newTracks.length === 1 ? "" : "s"}.`
        : "No new songs found; this playlist is already in your library.",
    );
    playlistUrlInput.value = "";
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    importButton.disabled = false;
    importButton.innerHTML = 'Import songs <span aria-hidden="true">↗</span>';
  }
});

categoryForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const category = categoryInput.value.trim();
  if (!category) {
    setStatus("Enter a name for your category.", true);
    return;
  }
  if (
    library.categories.some(
      (existing) => existing.toLocaleLowerCase() === category.toLocaleLowerCase(),
    )
  ) {
    setStatus("That category already exists.", true);
    return;
  }
  library.categories.push(category);
  categoryInput.value = "";
  setStatus(`Added category “${category}”.`);
  render();
});

function csvCell(value) {
  return `"${String(value).replaceAll('"', '""')}"`;
}

exportButton.addEventListener("click", () => {
  if (!library.tracks.length) {
    setStatus("Import songs before exporting a list.", true);
    return;
  }
  const rows = [["Title", "Channel", "Category", "YouTube URL"]];
  for (const category of library.categories) {
    for (const track of library.tracks.filter((song) => song.category === category)) {
      rows.push([
        track.title,
        track.channel || "",
        category,
        `https://www.youtube.com/watch?v=${track.videoId}`,
      ]);
    }
  }
  const csv = rows.map((row) => row.map(csvCell).join(",")).join("\r\n");
  const blob = new Blob([`\ufeff${csv}`], { type: "text/csv;charset=utf-8" });
  const downloadUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = downloadUrl;
  link.download = "svara-atlas-categorized-songs.csv";
  link.click();
  URL.revokeObjectURL(downloadUrl);
  setStatus("Downloaded your categorized song list.");
});

render();
