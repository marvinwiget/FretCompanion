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

const total = document.getElementById("chord-total");
function updateChordCount() {
    if (total) {
        const count = document.querySelectorAll('.chord-option:checked').length;
        total.textContent = `${count} chord${count === 1 ? "" : "s"} selected`;
    }
}
document.querySelectorAll(".chord-group").forEach((group) => {
    const selectAll = group.querySelector(".select-all-checkbox");
    const options = [...group.querySelectorAll(".chord-option")];
    function syncRow() {
        const count = options.filter((option) => option.checked).length;
        selectAll.checked = count === options.length;
        selectAll.indeterminate = count > 0 && count < options.length;
        group.querySelector(".row-count").textContent = `${count} / ${options.length} selected`;
        updateChordCount();
    }
    selectAll.addEventListener("change", () => {
        options.forEach((option) => { option.checked = selectAll.checked; });
        syncRow();
    });
    options.forEach((option) => option.addEventListener("change", syncRow));
    syncRow();
});
document.querySelectorAll(".retained-chord input").forEach((input) => {
    input.addEventListener("change", updateChordCount);
});
updateChordCount();

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
