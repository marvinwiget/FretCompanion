const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');

const script = readFileSync(join(__dirname, '../app/static/js/app.js'), 'utf8');

// Small DOM stand-ins let us exercise the actual script without a browser dependency.
function setup(hasForm = true) {
    const listeners = {};
    const windowListeners = {};
    const attributes = {};
    const button = { disabled: false, textContent: 'Search' };
    const progress = { hidden: true };
    const alerts = [{ hidden: false }, { hidden: false }];
    const form = {
        querySelector: () => button,
        querySelectorAll: () => alerts,
        addEventListener: (name, callback) => { listeners[name] = callback; },
        setAttribute: (name, value) => { attributes[name] = value; },
        removeAttribute: (name) => { delete attributes[name]; },
    };
    const elements = hasForm ? { 'search-form': form, 'search-progress': progress } : {};
    vm.runInNewContext(script, {
        document: {
            getElementById: (id) => elements[id] || null,
            querySelectorAll: () => [],
        },
        window: { addEventListener: (name, callback) => { windowListeners[name] = callback; } },
    });
    function submit() {
        const event = { prevented: false, preventDefault() { this.prevented = true; } };
        listeners.submit(event);
        return event;
    }
    return { button, progress, alerts, attributes, submit, windowListeners };
}

test('script also works on pages without a search form', () => {
    assert.doesNotThrow(() => setup(false));
});

test('initial page keeps its normal button and hides progress', () => {
    const ui = setup();
    assert.equal(ui.button.disabled, false);
    assert.equal(ui.button.textContent, 'Search');
    assert.equal(ui.progress.hidden, true);
});

test('first submission proceeds and announces loading', () => {
    const ui = setup();
    assert.equal(ui.submit().prevented, false);
    assert.equal(ui.button.disabled, true);
    assert.equal(ui.button.textContent, 'Searching…');
    assert.equal(ui.progress.hidden, false);
    assert.equal(ui.attributes['aria-busy'], 'true');
});

test('old errors are hidden while a new search runs', () => {
    const ui = setup();
    ui.submit();
    assert.ok(ui.alerts.every((alert) => alert.hidden));
});

test('repeated submissions are prevented', () => {
    const ui = setup();
    ui.submit();
    assert.equal(ui.submit().prevented, true);
    assert.equal(ui.submit().prevented, true);
});

test('back navigation restores the button, errors and progress state', () => {
    const ui = setup();
    ui.submit();
    ui.windowListeners.pageshow();
    assert.equal(ui.button.disabled, false);
    assert.equal(ui.button.textContent, 'Search');
    assert.equal(ui.progress.hidden, true);
    assert.equal(ui.attributes['aria-busy'], undefined);
    assert.ok(ui.alerts.every((alert) => !alert.hidden));
});

test('another search can run after back navigation', () => {
    const ui = setup();
    ui.submit();
    ui.windowListeners.pageshow();
    assert.equal(ui.submit().prevented, false);
    assert.equal(ui.button.disabled, true);
});
