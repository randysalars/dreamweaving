/**
 * Dreamweaving Christmas Video analytics helper.
 * Usage: include before GTM/gtag. Configure GTM GA4 event tags to read from dataLayer.
 */
(function (window, document) {
  const dataLayer = (window.dataLayer = window.dataLayer || []);
  const SESSION_KEY = "dw_session_id";
  const CLIENT_KEY = "dw_client_id";
  const seenScrolls = new Set();
  const seenTimers = new Set();
  let videoStarted = false;

  function uuid() {
    return "xxxxxx4xyx".replace(/[xy]/g, function (c) {
      const r = (Math.random() * 16) | 0;
      const v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  function getOrCreate(key) {
    try {
      const existing = window.localStorage.getItem(key);
      if (existing) return existing;
      const value = uuid();
      window.localStorage.setItem(key, value);
      return value;
    } catch (_) {
      return uuid();
    }
  }

  function readUrlParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name) || undefined;
  }

  function collectUtm() {
    return {
      utm_source: readUrlParam("utm_source"),
      utm_medium: readUrlParam("utm_medium"),
      utm_campaign: readUrlParam("utm_campaign"),
      utm_content: readUrlParam("utm_content"),
    };
  }

  const defaults = {
    session_id: getOrCreate(SESSION_KEY),
    client_id: getOrCreate(CLIENT_KEY),
    ...collectUtm(),
  };

  function trackEvent(event, params = {}) {
    dataLayer.push({
      event,
      stage: params.stage,
      message_type: params.message_type,
      cta_label: params.cta_label,
      placement: params.placement,
      video_id: params.video_id,
      amount: params.amount,
      currency: params.currency,
      preset: params.preset,
      transaction_id: params.transaction_id,
      ...defaults,
      ...params,
    });
  }

  function initPageView() {
    trackEvent("page_view_light", { stage: "awareness" });
  }

  function initScrollTracking() {
    function onScroll() {
      const doc = document.documentElement;
      const total = doc.scrollHeight - doc.clientHeight;
      if (total <= 0) return;
      const depth = Math.round((doc.scrollTop / total) * 100);
      [25, 50, 75, 100].forEach((mark) => {
        if (depth >= mark && !seenScrolls.has(mark)) {
          seenScrolls.add(mark);
          trackEvent(`scroll_${mark}`, { stage: "awareness" });
        }
      });
    }
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  function initTimers() {
    const marks = [
      { ms: 30000, name: "time_30s" },
      { ms: 90000, name: "time_90s" },
      { ms: 180000, name: "time_180s" },
    ];
    marks.forEach(({ ms, name }) => {
      window.setTimeout(() => {
        if (!seenTimers.has(name)) {
          seenTimers.add(name);
          trackEvent(name, { stage: "engagement" });
        }
      }, ms);
    });
    window.addEventListener("beforeunload", () => {
      if (!videoStarted) {
        trackEvent("exit_before_video", { stage: "engagement" });
      }
    });
  }

  function registerCTA(selector, meta = {}) {
    document.querySelectorAll(selector).forEach((el) => {
      el.addEventListener("click", () => {
        trackEvent("donation_cta_click", {
          stage: "intent",
          cta_label: meta.cta_label || el.dataset.ctaLabel || selector,
          message_type: meta.message_type || el.dataset.messageType,
          placement: meta.placement || el.dataset.placement,
        });
      });
    });
  }

  function trackDonationAmount(el) {
    el.addEventListener("click", () => {
      const amount = parseFloat(el.dataset.amount || el.value || 0);
      trackEvent("donation_amount_selected", {
        stage: "intent",
        amount: isNaN(amount) ? undefined : amount,
        currency: el.dataset.currency || "USD",
        preset: Boolean(el.dataset.preset),
      });
    });
  }

  function registerAmountSelectors(selector) {
    document.querySelectorAll(selector).forEach((el) => {
      trackDonationAmount(el);
    });
  }

  function trackPaypalOpened(meta = {}) {
    trackEvent("paypal_opened", { stage: "intent", ...meta });
  }

  function registerHtml5Video(videoEl, opts = {}) {
    if (!videoEl) return;
    const milestones = [0.25, 0.5, 0.75, 0.95];
    const fired = new Set();

    function pushProgress(ratio) {
      milestones.forEach((m) => {
        if (ratio >= m && !fired.has(m)) {
          fired.add(m);
          trackEvent(`video_${Math.round(m * 100)}`, {
            stage: "engagement",
            video_id: opts.video_id || videoEl.id,
            message_type: opts.message_type,
          });
        }
      });
      if (ratio >= 1 && !fired.has(1)) {
        fired.add(1);
        trackEvent("video_complete", {
          stage: "engagement",
          video_id: opts.video_id || videoEl.id,
          message_type: opts.message_type,
        });
      }
    }

    videoEl.addEventListener("play", () => {
      if (!fired.has("start")) {
        fired.add("start");
        videoStarted = true;
        trackEvent("video_start", {
          stage: "engagement",
          video_id: opts.video_id || videoEl.id,
          message_type: opts.message_type,
        });
      } else {
        trackEvent("video_replay", {
          stage: "reflection",
          video_id: opts.video_id || videoEl.id,
          message_type: opts.message_type,
        });
      }
    });

    videoEl.addEventListener("timeupdate", () => {
      const ratio = videoEl.currentTime / (videoEl.duration || 1);
      pushProgress(ratio);
    });

    videoEl.addEventListener("ended", () => pushProgress(1));
  }

  // Bootstrap defaults
  initPageView();
  initScrollTracking();
  initTimers();

  window.DreamweavingAnalytics = {
    trackEvent,
    registerCTA,
    registerAmountSelectors,
    trackPaypalOpened,
    registerHtml5Video,
    defaults,
  };
})(window, document);
