const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(
  path.join(__dirname, '../../visualization/dashboard/dashboard-i18n.js'), 'utf8',
);

function load(search, saved, blockedStorage = false) {
  const elements = new Map();
  const callbacks = new Map();
  const events = [];
  const buttons = ['en', 'ja'].map(lang => ({
    dataset: { lang },
    classList: { toggle(name, active) { this[name] = active; } },
    addEventListener(name, callback) { this[name] = callback; },
  }));
  const document = {
    documentElement: {},
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, { textContent: '', href: '' });
      return elements.get(id);
    },
    querySelectorAll(selector) {
      return selector === '.lang-toggle button' ? buttons : [];
    },
    addEventListener(name, callback) { callbacks.set(name, callback); },
    dispatchEvent(event) { events.push(event); },
  };
  const window = {
    location: { search },
    localStorage: {
      getItem(key) {
        assert.equal(key, 'dashboardLang');
        if (blockedStorage) throw new Error('Storage denied');
        return saved;
      },
      setItem(key, value) {
        assert.equal(key, 'dashboardLang');
        if (blockedStorage) throw new Error('Storage denied');
        saved = value;
      },
    },
  };
  const context = vm.createContext({
    window, document, URLSearchParams,
    CustomEvent: class {
      constructor(type, options) { this.type = type; this.detail = options.detail; }
    },
    fetch() { throw new Error('Language changes must not fetch source data'); },
  });
  vm.runInContext(source, context);
  callbacks.get('DOMContentLoaded')();
  return { window, document, elements, events, buttons, context, saved: () => saved };
}

for (const [query, saved, expected] of [
  ['', null, 'en'],
  ['', 'ja', 'ja'],
  ['', 'invalid', 'en'],
  ['?lang=ja', 'en', 'ja'],
  ['?lang=en', 'ja', 'en'],
  ['?lang=invalid', 'ja', 'ja'],
  ['?lang=', null, 'en'],
  ['?lang=%6Aa', null, 'ja'],
]) {
  const app = load(query, saved);
  assert.equal(app.window.dashboardI18n.getLang(), expected);
  assert.equal(app.document.documentElement.lang, expected);
  assert.equal(
    app.elements.get('i18n-back-link').href,
    expected === 'ja' ? '../index.ja.html' : '../index.html',
  );
  assert.equal(app.buttons.find(b => b.dataset.lang === expected).classList.active, true);
}

for (const query of ['', '?lang=ja', '?lang=en']) {
  const app = load(query, 'ja', true);
  assert.equal(app.window.dashboardI18n.getLang(), query === '?lang=ja' ? 'ja' : 'en');
  app.buttons[1].click();
  assert.equal(app.document.documentElement.lang, 'ja');
}

const app = load('?lang=ja', 'en');
const dictionaryKeys = vm.runInContext('Object.keys(STRINGS)', app.context);
for (const key of dictionaryKeys) {
  assert.equal(vm.runInContext(`Object.hasOwn(STRINGS[${JSON.stringify(key)}], 'en')`, app.context), true);
  assert.equal(vm.runInContext(`Object.hasOwn(STRINGS[${JSON.stringify(key)}], 'ja')`, app.context), true);
}
app.buttons[0].click();
assert.equal(app.saved(), 'en');
assert.equal(app.document.documentElement.lang, 'en');
assert.equal(app.elements.get('i18n-back-link').href, '../index.html');
assert.equal(app.events.at(-1).type, 'dashboard-lang-changed');
assert.equal(app.events.at(-1).detail.lang, 'en');
const count = app.events.length;
app.window.dashboardI18n.setLang('invalid');
assert.equal(app.events.length, count);
assert.equal(app.window.dashboardI18n.getLang(), 'en');
console.log('Dashboard locale precedence, navigation, toggle and storage cases passed.');
