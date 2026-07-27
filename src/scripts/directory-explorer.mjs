import {
  deriveFacetCounts,
  filterDirectoryRecords,
  parseDirectoryState,
  serializeDirectoryState,
} from "../lib/directory.mjs";
import {
  loadPagefind,
  searchPagefind,
} from "../lib/pagefind-client.mjs";
import { SITE_BASE } from "../lib/paths.mjs";

function routeKey(value) {
  const url = new URL(value, window.location.origin);
  return url.pathname.startsWith(`${SITE_BASE}/`)
    ? url.pathname.slice(SITE_BASE.length)
    : url.pathname;
}

class DirectoryExplorer extends HTMLElement {
  connectedCallback() {
    this.form = this.querySelector("[data-directory-form]");
    this.results = this.querySelector("[data-directory-results]");
    this.status = this.querySelector("[data-directory-status]");
    this.items = [...this.querySelectorAll("[data-directory-record]")].map(
      (element) => ({
        element,
        record: JSON.parse(element.dataset.directoryRecord),
      }),
    );
    this.requestId = 0;
    this.pagefindPromise = null;

    this.restoreState();
    this.form.addEventListener("input", () => this.update());
    this.form.addEventListener("change", () => this.update());
    this.form.addEventListener("reset", () => {
      window.setTimeout(() => this.update(), 0);
    });
    this.update({ replaceUrl: false });
  }

  state() {
    return parseDirectoryState(
      new URLSearchParams(new FormData(this.form)),
    );
  }

  restoreState() {
    const state = parseDirectoryState(
      new URL(window.location.href).searchParams,
    );
    this.form.elements.q.value = state.query;
    for (const checkbox of this.form.querySelectorAll(
      'input[type="checkbox"]',
    )) {
      checkbox.checked = Object.values(state)
        .filter(Array.isArray)
        .some((selected) => selected.includes(checkbox.value));
    }
  }

  updateUrl(state) {
    const url = new URL(window.location.href);
    url.search = serializeDirectoryState(state).toString();
    window.history.replaceState({}, "", url);
  }

  updateCounts(state) {
    const counts = deriveFacetCounts(
      this.items.map(({ record }) => record),
      state,
    );
    for (const count of this.querySelectorAll("[data-facet-count]")) {
      const [dimension, value] = count.dataset.facetCount.split(":");
      count.textContent = String(counts[dimension]?.[value] ?? 0);
    }
  }

  showRecords(ids) {
    let visible = 0;
    for (const { element, record } of this.items) {
      const show = ids.has(record.id);
      element.hidden = !show;
      visible += Number(show);
    }
    return visible;
  }

  resultMessage(count) {
    return this.dataset.resultsTemplate.replace("{count}", String(count));
  }

  announce(count) {
    this.status.textContent =
      count === 0 ? this.dataset.emptyMessage : this.resultMessage(count);
  }

  async update({ replaceUrl = true } = {}) {
    const state = this.state();
    const requestId = ++this.requestId;
    if (replaceUrl) {
      this.updateUrl(state);
    }
    this.updateCounts(state);

    const local = filterDirectoryRecords(
      this.items.map(({ record }) => record),
      state,
    );
    const localIds = new Set(local.map(({ id }) => id));
    this.showRecords(localIds);
    this.results.setAttribute("aria-busy", "true");
    this.status.textContent = this.dataset.loadingMessage;

    try {
      this.pagefindPromise ??= loadPagefind();
      const response = await searchPagefind(await this.pagefindPromise, state);
      if (requestId !== this.requestId || response.cancelled) {
        return;
      }
      const resultRoutes = new Set(
        response.results.map(({ url }) => routeKey(url)),
      );
      const pagefindIds = new Set(
        this.items
          .filter(
            ({ element, record }) =>
              localIds.has(record.id) &&
              resultRoutes.has(routeKey(element.querySelector("a").href)),
          )
          .map(({ record }) => record.id),
      );
      this.announce(this.showRecords(pagefindIds));
    } catch {
      if (requestId !== this.requestId) {
        return;
      }
      const count = this.showRecords(localIds);
      this.status.textContent = `${this.dataset.errorMessage} ${this.resultMessage(count)}`;
    } finally {
      if (requestId === this.requestId) {
        this.results.setAttribute("aria-busy", "false");
      }
    }
  }
}

if (!customElements.get("directory-explorer")) {
  customElements.define("directory-explorer", DirectoryExplorer);
}
