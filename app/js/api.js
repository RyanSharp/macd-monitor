function getArchive(ticker, last_date) {
    last_date = last_date ? last_date : 0;
    var xhr, response;
    return new Promise(function(resolve, reject) {
        xhr = new XMLHttpRequest();
        xhr.open("GET", "/api/stock_tracker/archive/" + ticker + "/" + last_date, true);
        xhr.onload = function(e) {
            response = JSON.parse(e.currentTarget.response);
            if (response.success) {
                resolve(response.results);
            } else {
                console.log(response);
                reject(response);
            }
        }
        xhr.onerror = function(e) {
            console.log(e);
            reject();
        }
        xhr.send();
    });
}

function getSymbolsList() {
    var xhr, response;
    return new Promise(function(resolve, reject) {
        xhr = new XMLHttpRequest();
        xhr.open("GET", "/api/stock_tracker/list_tickers", true);
        xhr.onload = function(e) {
            response = JSON.parse(e.currentTarget.response);
            if (response.success) {
                resolve(response.results);
            } else {
                console.log(response);
                reject(response);
            }
        }
        xhr.onerror = function(e) {
            console.log(e);
            reject();
        }
        xhr.send();
    });
}

function getFullSymbolArchive(ticker) {
    var archive = [], last_date = 0;
    return new Promise(function(resolve, reject) {
        function nextArchive() {
            getArchive(ticker, last_date).then(function(results) {
                if (results.length === 0) resolve(archive);
                results.map(function(result) {
                    archive.push(result);
                    last_date = result.date;
                });
                nextArchive();
            });
        }
        nextArchive();
    });
}