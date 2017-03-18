CORE_SCRIPTS = [
    "https://unpkg.com/react@15/dist/react.js",
    "https://unpkg.com/react-dom@15/dist/react-dom.js",
    "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.min.js",
];

APP_SCRIPTS = [
    "/api.js",
];

COMPONENT_SCRIPTS = [
    "/react/stock-profile.js",
]

function loadSource() {
    addScripts(CORE_SCRIPTS).then(function() {
        addScripts(API_SCRIPTS).then(function() {
            addScripts(COMPONENT_SCRIPTS);
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