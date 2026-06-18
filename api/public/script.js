// ── DOM References ────────────────────────────────────────────
const chatToggle = document.getElementById("chatToggle");
const chatToggleSecondary = document.getElementById("chatToggleSecondary");

// ── Bridge to Isolated Chatbot Web Component ──────────────────
const getChatbot = () => document.querySelector("bmc-chatbot-widget");

if (chatToggle) {
  chatToggle.addEventListener("click", () => {
    const chatbot = getChatbot();
    if (chatbot) chatbot.openChat();
  });
}

if (chatToggleSecondary) {
  chatToggleSecondary.addEventListener("click", () => {
    const chatbot = getChatbot();
    if (chatbot) chatbot.openChat();
  });
}

// ── Intersection Observer for Cards Animation ─────────────────
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("visible");
      revealObserver.unobserve(entry.target);
    }
  });
}, {
  threshold: 0.2,
});

const revealItems = document.querySelectorAll(".endpoint-card, .feature-card");
revealItems.forEach((item) => revealObserver.observe(item));

// ── Accordion Interaction for Info Cards ──────────────────────
const expandableCards = document.querySelectorAll(".endpoint-card, .feature-card");
expandableCards.forEach((card) => {
  card.addEventListener("click", () => {
    const isOpen = card.classList.toggle("open");
    card.setAttribute("aria-expanded", isOpen);
  });

  card.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      const isOpen = card.classList.toggle("open");
      card.setAttribute("aria-expanded", isOpen);
    }
  });
});
