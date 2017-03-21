CORE_SCRIPTS = [
    "https://unpkg.com/react@15/dist/react.js",
    "https://unpkg.com/react-dom@15/dist/react-dom.js",
    "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.min.js",
];

APP_SCRIPTS = [
    "/app/js/api.js",
    "/app/js/calculations.js",
    "/app/js/models/archive.js",
];

COMPONENT_SCRIPTS = [
    "/app/js/react/nav.js",
    "/app/js/react/stock-profile.js",
];

function loadSource(callback) {
    addScripts(CORE_SCRIPTS).then(function() {
        addScripts(APP_SCRIPTS).then(function() {
            addScripts(COMPONENT_SCRIPTS).then(function() {
                callback ? callback() : null;
            });;
        });
    });
}

function addScripts(scripts) {
    var head = document.getElementsByTagName("head")[0];
    return new Promise(function(resolve, reject) {
        var promises = scripts.map(function(api) {
            return new Promise(function(resolve, reject) {
                var scriptTag;
                scriptTag = document.createElement("script");
                scriptTag.setAttribute("src", api);
                scriptTag.setAttribute("type", "text/javascript");
                scriptTag.onload = resolve;
                scriptTag.onerror = reject;
                scriptTag.onreadystatechange = function(e) {
                    if (this.readyState === "complete") resolve();
                }
                head.appendChild(scriptTag);
            });
        });
        Promise.all(promises).then(resolve);
    });
}

function renderApp(node) {
    node = typeof(node) === "string" ? document.getElementById(node) : node;
    ReactDOM.render(React.createElement(Nav, {}), node);
}
