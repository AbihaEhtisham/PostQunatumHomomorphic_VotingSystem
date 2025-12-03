let selected = null;

const cards = document.querySelectorAll(".candidate-card");
const submitBtn = document.getElementById("submitBtn");
const selectedInput = document.getElementById("selected_candidate");

cards.forEach((card, index) => {
    card.addEventListener("click", () => {
        cards.forEach(c => c.classList.remove("selected"));
        card.classList.add("selected");

        selectedInput.value = index; // send index, not name
        submitBtn.disabled = false;
        submitBtn.classList.add("enabled");
    });
});

