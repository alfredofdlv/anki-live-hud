/* Anki Live HUD: no network, dependencies, card HTML access, or scheduler writes. */
(() => {
  "use strict";
  const root = document.documentElement;
  const byId = id => document.getElementById(id);
  const names = ["", "Again", "Hard", "Good", "Easy"];
  const motionPreference = window.matchMedia("(prefers-reduced-motion: reduce)");
  const values = new Map();
  const tweens = new Map();
  const deltaTimers = new Map();
  let previous = null;
  let config = { animations: true };
  let frame = null;
  let celebrationTimer = null;

  function motion() { return config.animations && !motionPreference.matches; }
  function format(key, value) {
    if (value === null || value === undefined) return "—";
    if (key === "accuracy") return value.toFixed(1) + "%";
    if (key === "progress") return Math.floor(value) + "%";
    return Math.round(value).toLocaleString();
  }
  function paint(key, value) {
    byId(key).textContent = format(key, value);
    if (key === "reviews") byId("goal-count").textContent = format(key, value);
  }
  function tick(now) {
    for (const [key, tween] of tweens) {
      const t = Math.min(1, (now - tween.start) / 380);
      const value = tween.from + (tween.to - tween.from) * (1 - (1 - t) ** 3);
      values.set(key, value);
      paint(key, value);
      if (t === 1) tweens.delete(key);
    }
    frame = tweens.size ? requestAnimationFrame(tick) : null;
  }
  function counter(key, target, animate) {
    const from = values.get(key);
    if (!animate || !motion() || from == null || target == null || from === target) {
      tweens.delete(key);
      values.set(key, target);
      paint(key, target);
      return;
    }
    tweens.set(key, { from, to: target, start: performance.now() });
    if (frame === null) frame = requestAnimationFrame(tick);
  }
  function delta(key, difference, animate) {
    const element = byId("delta-" + key);
    if (!element || !difference || !animate || !motion()) return;
    clearTimeout(deltaTimers.get(key));
    element.textContent = (difference > 0 ? "+" : "−") +
      (key === "accuracy" ? Math.abs(difference).toFixed(1) + "pp" : Math.abs(difference));
    element.classList.toggle("down", difference < 0);
    element.classList.add("shown");
    deltaTimers.set(key, setTimeout(() => element.classList.remove("shown"), 1250));
  }
  function clearFeedback() {
    for (const timer of deltaTimers.values()) clearTimeout(timer);
    deltaTimers.clear();
    document.querySelectorAll(".delta").forEach(el => el.classList.remove("shown"));
    clearTimeout(celebrationTimer);
    byId("celebration").classList.remove("active");
  }
  function update(payload) {
    config = payload.config;
    root.dataset.theme = config.theme;
    root.dataset.compact = String(Boolean(config.compact));
    root.dataset.motion = String(Boolean(motion()));
    byId("distribution").hidden = !config.show_distribution;
    if (!motion()) clearFeedback();
    const stats = payload.stats;
    if (!stats) return;
    const sameDay = previous && previous.day === stats.day;
    const animate = Boolean(sameDay);
    if (!sameDay) clearFeedback();
    for (const key of ["reviews", "correct", "again", "accuracy", "remaining", "progress"]) {
      counter(key, stats[key], animate);
      if (sameDay && stats[key] != null && previous[key] != null) {
        delta(key, stats[key] - previous[key], animate);
      }
    }
    byId("unique_cards").textContent = stats.unique_cards.toLocaleString();
    byId("goal").textContent = stats.goal.toLocaleString();
    byId("goal-fill").style.transform = `scaleX(${stats.progress / 100})`;
    byId("goal-meter").setAttribute("aria-valuenow", String(stats.progress));
    byId("accuracy-fill").style.transform = `scaleX(${(stats.accuracy || 0) / 100})`;
    byId("deck").textContent = stats.deck;
    byId("deck").title = stats.deck;
    byId("goal-message").textContent = stats.reviews >= stats.goal ? "Daily goal reached. Nicely done." :
      `${(stats.goal - stats.reviews).toLocaleString()} answers to your goal`;
    for (const key of ["again", "hard", "good", "easy"]) {
      byId("mix-" + key).style.width = `${stats.reviews ? stats[key] / stats.reviews * 100 : 0}%`;
      byId("mix-count-" + key).textContent = stats[key].toLocaleString();
    }
    const undone = sameDay && stats.reviews < previous.reviews;
    byId("last-answer").textContent = stats.last_rating ?
      `${names[stats.last_rating]}${undone ? " · restored" : ""}` : "Ready when you are";
    const changed = sameDay && stats.reviews !== previous.reviews;
    byId("status").textContent = changed ?
      (undone ? "Review history restored." : `${names[stats.last_rating] || "Answer"} · ${stats.reviews} reviews today`) : "";
    if (sameDay && previous.goal === stats.goal && previous.reviews < stats.goal &&
        stats.reviews >= stats.goal && payload.reason === "answer") {
      byId("status").textContent = "Daily goal reached.";
      if (motion()) {
        byId("celebration").classList.add("active");
        clearTimeout(celebrationTimer);
        celebrationTimer = setTimeout(() => byId("celebration").classList.remove("active"), 1100);
      }
    }
    previous = { ...stats };
  }
  motionPreference.addEventListener("change", () => {
    root.dataset.motion = String(Boolean(motion()));
    if (!motion()) {
      clearFeedback();
      for (const [key, tween] of tweens) { values.set(key, tween.to); paint(key, tween.to); }
      tweens.clear();
    }
  });
  document.querySelectorAll("[data-command]").forEach(button => {
    button.addEventListener("click", () => {
      if (typeof pycmd === "function") pycmd("hud:" + button.dataset.command);
    });
  });
  window.AnkiLiveHUD = {
    update,
    connect: () => { if (typeof pycmd === "function") pycmd("hud:ready"); },
    setStatus: message => { byId("status").textContent = message; },
  };
})();
