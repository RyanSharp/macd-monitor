function parseHashAndQuery() {
    var hash, query, hashPath, a;
    a = document.createElement("a");
    a.setAttribute("href", window.location.href);
    hash = a.hash.split("/").slice(1).join("/").split("?");
    query = {};
    if (hash.length > 1) {
        hash[1].split("&").map(function(pairs) {
            pairs = pairs.split("=");
            query[decodeURIComponent(pairs[0])] = decodeURIComponent(pairs[1]);
        });
    }
    return {
        path: hash[0].split("/"),
        params: query,
    }
}

function generateUrl(path, query) {
    return "#/" + path.join("/") + (query ? "?" + Object.keys(query).map(function(k) {return encodeURIComponent(k) + "=" + encodeURIComponent(query[k])}).join("&") : "");
}