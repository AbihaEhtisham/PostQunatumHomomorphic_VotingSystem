let selected = null;

const cards = document.querySelectorAll(".candidate-card");
const submitBtn = document.getElementById("submitBtn");
const selectedInput = document.getElementById("selected_candidate");

cards.forEach(card => {
    card.addEventListener("click", () => {

        cards.forEach(c => c.classList.remove("selected"));
        card.classList.add("selected");

        selected = card.getAttribute("data-candidate");
        selectedInput.value = selected;

        submitBtn.disabled = false;
        submitBtn.classList.add("enabled");
    });
});
