CORE_SCRIPTS = [
    "https://unpkg.com/react@15/dist/react.js",
    "https://unpkg.com/react-dom@15/dist/react-dom.js",
    "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.min.js",
];

APP_SCRIPTS = [
    "/api.js",
    "/calculations.js",
    "/models/archive.js",
];

COMPONENT_SCRIPTS = [
    "/react/nav.js",
    "/react/stock-profile.js",
];

function loadSource(callback) {
    addScripts(CORE_SCRIPTS).then(function() {
        addScripts(API_SCRIPTS).then(function() {
            addScripts(COMPONENT_SCRIPTS).then(function() {
                callback ? callback() : null;
            });;
        });
    });
}

function addScripts(scripts) {
    return new Promise(function(resolve, reject) {
        var promises = Object.keys(scripts).map(function(api) {
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