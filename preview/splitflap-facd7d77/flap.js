/* Shared 4x15 split-flap board for the BRUNCH, PLEASE! mockup. Draft only. */
(function (global) {
  const COLS = 15;
  const ROWS = 4;
  const ALLOWED = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !?.,'-&#@:";
  const ALLOWED_SET = new Set(ALLOWED.split(""));

  function sanitize(raw) {
    const typo = String(raw || "")
      .replace(/[\u2018\u2019]/g, "'")
      .replace(/[\u2013\u2014]/g, "-")
      .toUpperCase();
    let out = "";
    for (const ch of typo) {
      if (ALLOWED_SET.has(ch)) out += ch;
      if (out.length >= 60) break;
    }
    return out;
  }

  function wrapLines(text) {
    const words = text.trim().replace(/ +/g, " ").split(" ").filter(Boolean);
    const lines = [];
    let splitWord = false;
    let line = "";

    function pushLine() {
      if (line) {
        lines.push(line);
        line = "";
      }
    }

    function addPiece(piece) {
      if (!line) {
        line = piece;
        return;
      }
      if (line.length + 1 + piece.length <= COLS) {
        line += " " + piece;
      } else {
        pushLine();
        line = piece;
      }
    }

    for (const word of words) {
      if (word.length <= COLS) {
        addPiece(word);
      } else {
        splitWord = true;
        let rest = word;
        while (rest.length > COLS) {
          addPiece(rest.slice(0, COLS));
          pushLine();
          rest = rest.slice(COLS);
        }
        if (rest) addPiece(rest);
      }
    }
    pushLine();
    const overflow = lines.length > ROWS;
    const used = lines.slice(0, ROWS);
    const top = Math.floor((ROWS - used.length) / 2);
    const grid = Array.from({ length: ROWS }, () => " ".repeat(COLS));
    used.forEach((l, i) => {
      grid[top + i] = (l + " ".repeat(COLS)).slice(0, COLS);
    });
    return {
      lines: grid,
      overflow,
      splitWord,
      usedRows: used.length,
      rawLines: lines,
    };
  }

  function layout(raw) {
    const text = sanitize(raw);
    if (!text.trim()) {
      return {
        text,
        lines: Array.from({ length: ROWS }, () => " ".repeat(COLS)),
        overflow: false,
        splitWord: false,
        usedRows: 0,
        rawLines: [],
        flat: " ".repeat(ROWS * COLS),
      };
    }
    const wrapped = wrapLines(text);
    return {
      text,
      ...wrapped,
      flat: wrapped.lines.join(""),
    };
  }

  function makeCell(ch) {
    const cell = document.createElement("div");
    cell.className = "sf-cell";
    cell.innerHTML =
      '<div class="sf-face"><span class="sf-letter"></span></div>' +
      '<div class="sf-fly sf-fly-top" aria-hidden="true"><span class="sf-letter"></span></div>' +
      '<div class="sf-fly sf-fly-bot" aria-hidden="true"><span class="sf-letter"></span></div>' +
      '<div class="sf-seam"></div>';
    setCellChar(cell, ch || " ", false);
    return cell;
  }

  function setSpans(cell, selector, ch) {
    cell.querySelectorAll(selector).forEach((el) => {
      el.textContent = ch === " " ? "" : ch;
    });
  }

  function setCellChar(cell, ch, animate) {
    const next = ch || " ";
    const prev = cell.dataset.ch || " ";
    if (!animate || prev === next) {
      cell.dataset.ch = next;
      setSpans(cell, ".sf-face .sf-letter", next);
      cell.classList.remove("is-flipping");
      return;
    }
    cell.dataset.ch = next;
    setSpans(cell, ".sf-fly-top .sf-letter", prev);
    setSpans(cell, ".sf-fly-bot .sf-letter", next);
    setSpans(cell, ".sf-face .sf-letter", next);
    cell.classList.remove("is-flipping");
    void cell.offsetWidth;
    cell.classList.add("is-flipping");
    window.setTimeout(() => {
      cell.classList.remove("is-flipping");
    }, 520);
  }

  function sizeBoard(root) {
    const cell = root.querySelector(".sf-cell");
    if (!cell) return;
    const w = cell.getBoundingClientRect().width;
    const compact = root.classList.contains("is-compact");
    const tiny = root.classList.contains("is-tiny");
    const ratio = tiny ? 1.3 : compact ? 1.32 : 1.38;
    const h = Math.max(tiny ? 16 : compact ? 20 : 24, Math.round(w * ratio));
    const fs = Math.max(tiny ? 10 : compact ? 12 : 14, Math.round(h * 0.72));
    root.style.setProperty("--ch", h + "px");
    root.style.setProperty("--fs", fs + "px");
  }

  function mount(root, opts) {
    opts = opts || {};
    root.classList.add("sf-board");
    if (opts.compact) root.classList.add("is-compact");
    if (opts.tiny) root.classList.add("is-tiny");
    root.innerHTML = "";
    const frame = document.createElement("div");
    frame.className = "sf-frame";
    const grid = document.createElement("div");
    grid.className = "sf-grid";
    const cells = [];
    for (let r = 0; r < ROWS; r++) {
      const row = document.createElement("div");
      row.className = "sf-row";
      for (let c = 0; c < COLS; c++) {
        const cell = makeCell(" ");
        row.appendChild(cell);
        cells.push(cell);
      }
      grid.appendChild(row);
    }
    frame.appendChild(grid);
    root.appendChild(frame);
    root._sf = { cells, current: " ".repeat(ROWS * COLS), opts };
    const resize = () => sizeBoard(root);
    resize();
    requestAnimationFrame(resize);
    if (typeof ResizeObserver !== "undefined" && !root._sfRo) {
      root._sfRo = new ResizeObserver(resize);
      root._sfRo.observe(root);
    }
    return root;
  }

  function setBoard(root, textOrLayout, opts) {
    if (!root._sf) mount(root, opts);
    const laid = typeof textOrLayout === "string" || textOrLayout == null
      ? layout(textOrLayout || "")
      : textOrLayout;
    const next = laid.flat || laid.lines.join("");
    const animate = !root._sf.opts || root._sf.opts.animate !== false;
    const doAnim = animate && !(opts && opts.animate === false);
    const prev = root._sf.current;
    let delay = 0;
    for (let i = 0; i < ROWS * COLS; i++) {
      const ch = next[i] || " ";
      if ((prev[i] || " ") === ch) {
        setCellChar(root._sf.cells[i], ch, false);
        continue;
      }
      const cell = root._sf.cells[i];
      if (doAnim) {
        const t = delay;
        delay = Math.min(delay + 18, 420);
        window.setTimeout(() => setCellChar(cell, ch, true), t);
      } else {
        setCellChar(cell, ch, false);
      }
    }
    root._sf.current = next;
    return laid;
  }

  global.SplitFlap = {
    COLS,
    ROWS,
    ALLOWED,
    sanitize,
    layout,
    mount,
    set: setBoard,
  };
})(window);
