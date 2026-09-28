/* Velanix Sourcing — progressive enhancement. Every form also works without JS. */
(function () {
  "use strict";

  // ---- mobile nav & mega menu ----
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open);
    });
  }
  document.querySelectorAll(".mega-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var li = btn.closest(".has-mega");
      var open = li.classList.toggle("open");
      btn.setAttribute("aria-expanded", open);
    });
  });
  document.addEventListener("click", function (e) {
    document.querySelectorAll(".has-mega.open").forEach(function (li) {
      if (!li.contains(e.target) && window.innerWidth > 960) {
        li.classList.remove("open");
        li.querySelector(".mega-toggle").setAttribute("aria-expanded", "false");
      }
    });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") document.querySelectorAll(".has-mega.open").forEach(function (li) { li.classList.remove("open"); });
  });

  // ---- validation helpers ----
  var lang = document.documentElement.lang;
  var MSG = lang === "de" ? "Dieses Feld ist erforderlich." : "This field is required.";
  var MSG_EMAIL = lang === "de" ? "Bitte geben Sie eine gültige E-Mail-Adresse ein." : "Please enter a valid email address.";

  function setError(field, msg) {
    field.classList.add("has-error");
    var p = field.querySelector(".field-error");
    if (!p) { p = document.createElement("p"); p.className = "field-error"; field.appendChild(p); }
    p.textContent = msg;
  }
  function clearError(field) {
    field.classList.remove("has-error");
    var p = field.querySelector(".field-error");
    if (p) p.remove();
  }
  function validate(scope) {
    var firstBad = null;
    scope.querySelectorAll("input[required], select[required], textarea[required]").forEach(function (el) {
      var field = el.closest(".field");
      if (!field) return;
      var ok = el.type === "checkbox" ? el.checked : el.value.trim() !== "";
      var msg = MSG;
      if (ok && el.type === "email" && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(el.value.trim())) { ok = false; msg = MSG_EMAIL; }
      if (ok) clearError(field); else { setError(field, msg); firstBad = firstBad || el; }
    });
    scope.querySelectorAll("fieldset[data-required]").forEach(function (fs) {
      if (fs.querySelector("input:checked")) clearError(fs);
      else { setError(fs, MSG); firstBad = firstBad || fs.querySelector("input"); }
    });
    if (firstBad) {
      firstBad.closest(".field").scrollIntoView({ behavior: "smooth", block: "center" });
      if (firstBad.focus) firstBad.focus({ preventScroll: true });
    }
    return !firstBad;
  }
  document.addEventListener("change", function (e) {
    var field = e.target.closest && e.target.closest(".has-error");
    if (field && (e.target.checked || (e.target.value && e.target.value.trim()))) clearError(field);
  });

  document.querySelectorAll("form[data-validate]").forEach(function (form) {
    form.addEventListener("submit", function (e) { if (!validate(form)) e.preventDefault(); });
  });

  // ---- multi-step RFQ form ----
  document.querySelectorAll("form[data-stepper]").forEach(function (form) {
    var panels = Array.prototype.slice.call(form.querySelectorAll(".step-panel"));
    var inds = form.querySelectorAll("[data-step-ind]");
    var prev = form.querySelector("[data-prev]");
    var next = form.querySelector("[data-next]");
    var submit = form.querySelector("[data-submit]");
    var current = 0;

    function show(i, scroll) {
      current = i;
      panels.forEach(function (p, k) { p.classList.toggle("active", k === i); });
      inds.forEach(function (el, k) { el.classList.toggle("active", k === i); el.classList.toggle("done", k < i); });
      prev.hidden = i === 0;
      next.hidden = i === panels.length - 1;
      submit.hidden = i !== panels.length - 1;
      if (scroll) form.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    next.addEventListener("click", function () { if (validate(panels[current])) show(current + 1, true); });
    prev.addEventListener("click", function () { show(current - 1, true); });
    form.addEventListener("submit", function (e) {
      for (var i = 0; i < panels.length; i++) {
        if (!validate(panels[i])) { e.preventDefault(); show(i, false); validate(panels[i]); return; }
      }
      submit.disabled = true;
    });
    // Enter in a text input advances instead of submitting early.
    form.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && e.target.tagName === "INPUT" && current < panels.length - 1) { e.preventDefault(); next.click(); }
    });

    // After a server-side validation error, open the first step containing an error.
    var errPanel = panels.findIndex(function (p) { return p.querySelector(".has-error"); });
    show(errPanel >= 0 ? errPanel : 0, false);

    // ---- live summary ----
    var list = document.querySelector("[data-summary-list]");
    var empty = document.querySelector("[data-summary-empty]");
    var fileInput = form.querySelector("input[type=file]");
    var fileList = form.querySelector(".file-list");

    function fmtSize(b) { return b > 1048576 ? (b / 1048576).toFixed(1) + " MB" : Math.max(1, Math.round(b / 1024)) + " KB"; }

    function renderSummary() {
      if (!list) return;
      var rows = [];
      var seen = {};
      form.querySelectorAll("[data-summary]").forEach(function (el) {
        var label = el.getAttribute("data-summary");
        var val = "";
        if (el.type === "radio" || el.type === "checkbox") { if (!el.checked) return; val = el.getAttribute("data-label"); }
        else if (el.tagName === "SELECT") { if (!el.value) return; val = el.options[el.selectedIndex].text; }
        else { val = el.value.trim(); if (!val) return; }
        if (el.name === "quantity") {
          var unit = form.querySelector("[name=quantity_unit]");
          if (unit) val += " " + unit.options[unit.selectedIndex].text;
        }
        if (el.name === "target_price") {
          var cur = form.querySelector("[name=currency]");
          if (cur) val += " " + cur.value;
        }
        if (seen[label] !== undefined) rows[seen[label]][1] += ", " + val;
        else { seen[label] = rows.length; rows.push([label, val]); }
      });
      if (fileInput && fileInput.files.length) rows.push([list.getAttribute("data-files-label"), fileInput.files.length + " ×"]);
      list.innerHTML = "";
      rows.forEach(function (r) {
        var d = document.createElement("div");
        var dt = document.createElement("dt"); dt.textContent = r[0];
        var dd = document.createElement("dd"); dd.textContent = r[1];
        d.appendChild(dt); d.appendChild(dd); list.appendChild(d);
      });
      if (empty) empty.hidden = rows.length > 0;
    }
    form.addEventListener("input", renderSummary);
    form.addEventListener("change", renderSummary);
    renderSummary();

    // ---- drag & drop file list ----
    if (fileInput) {
      var zone = fileInput.closest(".dropzone");
      ["dragenter", "dragover"].forEach(function (ev) { zone.addEventListener(ev, function () { zone.classList.add("drag"); }); });
      ["dragleave", "drop"].forEach(function (ev) { zone.addEventListener(ev, function () { zone.classList.remove("drag"); }); });
      fileInput.addEventListener("change", function () {
        fileList.innerHTML = "";
        Array.prototype.forEach.call(fileInput.files, function (f) {
          var li = document.createElement("li");
          var a = document.createElement("span"); a.textContent = f.name;
          var b = document.createElement("span"); b.textContent = fmtSize(f.size);
          li.appendChild(a); li.appendChild(b); fileList.appendChild(li);
        });
      });
    }
  });

  var params = new URLSearchParams(location.search);

  // ---- homepage quick-quote: go straight to the category form ----
  document.querySelectorAll("form[data-quick]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      var sel = form.querySelector("[name=category]");
      var opt = sel.options[sel.selectedIndex];
      if (!opt || !opt.getAttribute("data-url")) return;
      e.preventDefault();
      var q = new URLSearchParams();
      ["quantity", "delivery_country"].forEach(function (n) { var v = form.elements[n].value.trim(); if (v) q.set(n, v); });
      location.href = opt.getAttribute("data-url") + (q.toString() ? "?" + q : "") + "#rfq";
    });
  });

  // ---- pre-fill fields passed in the URL (from the quick-quote box) ----
  ["quantity", "delivery_country"].forEach(function (n) {
    var el = document.querySelector("form[data-stepper] [name=" + n + "]");
    if (el && !el.value && params.get(n)) { el.value = params.get(n); el.dispatchEvent(new Event("change", { bubbles: true })); }
  });

  // ---- static site (GitHub Pages): submit to a form service, or fall back to email ----
  var FAIL = lang === "de" ? "Senden fehlgeschlagen. Bitte versuchen Sie es erneut oder schreiben Sie uns eine E-Mail." : "Sending failed. Please try again or email us directly.";
  var ATTACH = lang === "de" ? "Bitte hängen Sie Ihre Zeichnungen an diese E-Mail an." : "Please attach your drawings to this email.";

  function labelOf(el) {
    if (el.getAttribute("data-summary")) return el.getAttribute("data-summary");
    var f = el.closest(".field");
    var l = f && f.querySelector("label, legend");
    return l ? l.textContent.replace("*", "").trim() : el.name;
  }
  function makeRef() {
    var d = new Date();
    return "VX-" + d.getFullYear() + String(d.getMonth() + 1).padStart(2, "0") + String(d.getDate()).padStart(2, "0") +
      "-" + Math.random().toString(36).slice(2, 6).toUpperCase();
  }

  document.querySelectorAll("form[data-static-form]").forEach(function (form) {
    // Registered after the validation listeners, so e.defaultPrevented means validation failed.
    form.addEventListener("submit", function (e) {
      if (e.defaultPrevented) return;
      e.preventDefault();
      if (form.elements._gotcha && form.elements._gotcha.value) return;
      var ref = makeRef();
      var subject = form.getAttribute("data-subject") + " · " + ref;
      var thanks = form.getAttribute("data-thanks") + "?ref=" + ref + "&kind=" + form.getAttribute("data-kind");
      var endpoint = form.getAttribute("data-endpoint");
      var buttons = form.querySelectorAll("button[type=submit]");
      buttons.forEach(function (b) { b.disabled = true; });

      if (endpoint) {
        var fd = new FormData(form);
        fd.append("reference", ref);
        fd.append("_subject", subject);
        fd.append("page", location.pathname);
        var send = function (data) { return fetch(endpoint, { method: "POST", body: data, headers: { Accept: "application/json" } }); };
        send(fd).then(function (r) {
          if (r.ok) return r;
          // Free form-service plans reject file uploads: retry without attachments.
          if (fd.has("attachments")) { fd.delete("attachments"); fd.append("attachments_note", "Files not uploaded - request drawings by email"); return send(fd); }
          return r;
        }).then(function (r) {
          if (!r.ok) throw new Error(r.status);
          location.href = thanks;
        }).catch(function () {
          buttons.forEach(function (b) { b.disabled = false; });
          var alert = form.querySelector(".form-alert") || form.insertBefore(document.createElement("div"), form.firstChild);
          alert.className = "form-alert"; alert.setAttribute("role", "alert"); alert.textContent = FAIL;
          alert.scrollIntoView({ behavior: "smooth", block: "center" });
        });
        return;
      }

      // No endpoint configured: open a pre-filled email with the structured request.
      var lines = ["Reference: " + ref, ""], seen = {}, hasFiles = false;
      Array.prototype.forEach.call(form.elements, function (el) {
        if (!el.name || el.name === "_gotcha" || el.name === "consent" || el.tagName === "BUTTON") return;
        if (el.type === "file") { hasFiles = hasFiles || el.files.length > 0; return; }
        if ((el.type === "checkbox" || el.type === "radio") && !el.checked) return;
        var val = el.getAttribute("data-label") || (el.tagName === "SELECT" && el.value ? el.options[el.selectedIndex].text : el.value);
        if (!val || !val.trim()) return;
        var key = el.type === "hidden" ? el.name : labelOf(el);
        if (seen[key] !== undefined) lines[seen[key]] += ", " + val.trim();
        else { seen[key] = lines.length; lines.push(key + ": " + val.trim()); }
      });
      if (hasFiles) lines.push("", ATTACH);
      location.href = "mailto:" + form.getAttribute("data-mailto") + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\n"));
      setTimeout(function () { location.href = thanks; }, 1200);
    });
  });

  // ---- static thank-you page ----
  var thanksBox = document.querySelector("[data-thanks-static]");
  if (thanksBox) {
    var ref = params.get("ref");
    if (ref && /^VX-[\w-]{4,20}$/.test(ref)) {
      thanksBox.querySelector("[data-ref]").textContent = ref;
      thanksBox.querySelector("[data-ref-box]").hidden = false;
    }
    var kind = params.get("kind") === "supplier" ? "supplier" : "buyer";
    thanksBox.querySelectorAll("[data-kind-text]").forEach(function (el) { el.hidden = el.getAttribute("data-kind-text") !== kind; });
  }
})();
