// Runs after HTML has been parsed because the script uses defer.
const rangeField = document.getElementById("time_range_field");
if (rangeField) {
    const updateRange = () => {
        const selected = document.querySelector('input[name="result_type"]:checked');
        rangeField.hidden = selected?.value !== "top_songs";
    };
    document.querySelectorAll('input[name="result_type"]').forEach((radio) => {
        radio.addEventListener("change", updateRange);
    });
    updateRange();
}

// Chord selection stays in ordinary form checkboxes for Flask to receive.
const picker = document.getElementById("chord-picker");
if (picker) {
    const showAccidentals = document.getElementById("show-accidentals");
    const selectedList = document.getElementById("selected-chords");
    const total = document.getElementById("chord-total");
    const root = document.getElementById("chord-root");
    const type = document.getElementById("chord-type");
    const status = document.getElementById("chord-builder-status");
    const groups = [...picker.querySelectorAll(".chord-group")];
    const options = () => [...picker.querySelectorAll(".chord-option")];
    const visibleOptions = (group) => [...group.querySelectorAll(".chord-option")]
        .filter((input) => !input.closest("label").hidden);

    function updateSelection() {
        const selected = options().filter((input) => input.checked);
        total.textContent = `${selected.length} chord${selected.length === 1 ? "" : "s"} selected`;
        selectedList.replaceChildren();
        selected.forEach((input) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "selected-chord";
            button.textContent = `${input.value} ×`;
            button.setAttribute("aria-label", `Remove ${input.value}`);
            button.addEventListener("click", () => {
                const index = [...selectedList.children].indexOf(button);
                input.checked = false;
                updateSelection();
                // Keep keyboard focus near the removed chip.
                const next = selectedList.children[index] || selectedList.lastElementChild;
                (next || showAccidentals).focus();
            });
            selectedList.append(button);
        });
        if (selected.length === 0) selectedList.textContent = "No chords selected yet.";
        groups.forEach((group) => {
            const visible = visibleOptions(group);
            const checked = visible.filter((input) => input.checked).length;
            const selectAll = group.querySelector(".select-all-checkbox");
            selectAll.checked = visible.length > 0 && checked === visible.length;
            selectAll.indeterminate = checked > 0 && checked < visible.length;
            const count = group.querySelectorAll(".chord-option:checked").length;
            group.querySelector(".row-count").textContent = `${count} selected`;
        });
    }

    function updateVisibility() {
        picker.querySelectorAll("[data-accidental]").forEach((label) => {
            label.hidden = !showAccidentals.checked;
        });
        updateSelection();
    }

    picker.addEventListener("change", (event) => {
        if (event.target.matches(".chord-option")) updateSelection();
    });
    groups.forEach((group) => {
        group.querySelector(".select-all-checkbox").addEventListener("change", (event) => {
            visibleOptions(group).forEach((input) => { input.checked = event.target.checked; });
            updateSelection();
        });
    });
    showAccidentals.addEventListener("change", updateVisibility);
    function updatePreview() {
        document.getElementById("chord-preview").textContent = root.value + type.value;
        status.textContent = "";
    }
    root.addEventListener("change", updatePreview);
    type.addEventListener("change", updatePreview);
    document.getElementById("add-chord").addEventListener("click", () => {
        const chord = root.value + type.value;
        let input = options().find((option) => option.value === chord);
        if (input?.checked) {
            status.textContent = `${chord} is already selected.`;
            return;
        }
        if (!input) {
            const label = document.createElement("label");
            label.className = "chord-choice retained-chord";
            input = document.createElement("input");
            input.type = "checkbox";
            input.name = "chords";
            input.value = chord;
            input.className = "chord-option";
            const text = document.createElement("span");
            text.textContent = chord;
            label.append(input, text);
            document.getElementById("custom-chords").append(label);
        }
        input.checked = true;
        updateSelection();
        status.textContent = `${chord} added. Save your guitar profile to keep it.`;
    });
    document.getElementById("accidental-control").hidden = false;
    document.getElementById("selected-chords-panel").hidden = false;
    document.getElementById("chord-builder").hidden = false;
    updatePreview();
    updateVisibility();
    // Restore counts after the browser restores form state via Back/Forward.
    window.addEventListener("pageshow", updateVisibility);
}

// Keep the initial order so turning sorting off restores the search results.
const sortButton = document.getElementById("sort-match");
const results = document.getElementById("song-results");

if (sortButton && results) {
    const originalCards = [...results.querySelectorAll(".song-card")];
    const sortStatus = document.getElementById("sort-status");
    const sortState = sortButton.querySelector(".sort-state");
    let sortEnabled = false;

    function getMatchScore(card) {
        const value = card.dataset.match;
        const score = Number(value);

        // Missing scores go below every scored song, including a 0% match.
        if (!value || !Number.isFinite(score)) {
            return -Infinity;
        }
        return score;
    }

    sortButton.hidden = false;
    sortButton.addEventListener("click", () => {
        sortEnabled = !sortEnabled;
        const cards = [...originalCards];

        if (sortEnabled) {
            cards.sort((first, second) => {
                const firstScore = getMatchScore(first);
                const secondScore = getMatchScore(second);

                // Equal scores keep their original order.
                if (firstScore === secondScore) {
                    return 0;
                }
                return secondScore - firstScore;
            });
        }

        results.append(...cards);
        sortButton.setAttribute("aria-pressed", String(sortEnabled));
        sortState.textContent = sortEnabled ? "On" : "Off";
        sortStatus.textContent = sortEnabled
            ? "Sorted by highest match. Tracks without a score appear last."
            : "Original track order restored.";
    });
}

// Save without navigating away from the search results.
const saveForms = [...document.querySelectorAll(".save-track-form")];
let savePending = false;
saveForms.forEach((form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (savePending) return;

        // Session cookies contain the entire list; avoid overlapping writes.
        savePending = true;
        saveForms.forEach((item) => { item.querySelector("button").disabled = true; });
        const status = form.querySelector(".save-status");
        status.textContent = "Saving…";

        try {
            const response = await fetch(form.action, {
                method: "POST",
                headers: { Accept: "application/json" },
                body: new FormData(form),
            });
            if (!response.ok) throw new Error("Save request failed");
            const result = await response.json();
            if (typeof result.saved !== "boolean") throw new Error("Invalid save response");

            // A recent-listen search can show the same track more than once.
            saveForms.filter((item) => item.action === form.action).forEach((item) => {
                const button = item.querySelector("button");
                button.textContent = result.saved ? "Unsave" : "Save";
                button.setAttribute("aria-pressed", String(result.saved));
                item.querySelector(".save-status").textContent = result.saved ? "Saved." : "Removed.";
            });
        } catch (error) {
            status.textContent = "Couldn’t confirm the change. Refresh to check its status.";
        } finally {
            savePending = false;
            saveForms.forEach((item) => { item.querySelector("button").disabled = false; });
        }
    });
});

// Give immediate feedback while the normal search POST is running.
const searchForm = document.getElementById("search-form");
if (searchForm) {
    const searchButton = searchForm.querySelector('button[type="submit"]');
    const progress = document.getElementById("search-progress");
    const originalLabel = searchButton.textContent;
    let searching = false;
    searchForm.addEventListener("submit", (event) => {
        if (searching) {
            event.preventDefault();
            return;
        }
        searching = true;
        searchButton.disabled = true;
        searchButton.textContent = "Searching…";
        searchForm.setAttribute("aria-busy", "true");
        searchForm.querySelectorAll('[role="alert"]').forEach((message) => { message.hidden = true; });
        progress.hidden = false;
    });
    window.addEventListener("pageshow", () => {
        searching = false;
        searchButton.disabled = false;
        searchButton.textContent = originalLabel;
        searchForm.removeAttribute("aria-busy");
        progress.hidden = true;
        searchForm.querySelectorAll('[role="alert"]').forEach((message) => { message.hidden = false; });
    });
}
