class Nav extends React.Component {
    constructor(props) {
        super(props);
    }
    componentDidMount() {
        /*
         * Application is too small to justify using routing framework, simple mechanism
         * for handling state changes using the hash of the URL
         * App state is handled on this react element.
         */
        var a = document.createElement("a");
        window.onhashchange = function(e) {
            var hash, query, hashPath;
            a.setAttribute("href", window.location.href);
            hash = a.hash.split("/").slice(1).join("/").split("?");
            query = {};
            hash[1].split("&").map(function(pairs) {
                pairs = pairs.split("=");
                query[decodeURIComponent(pairs[0])] = decodeURIComponent(pairs[1]);
            });
            this.setState({
                path: hash[0].split("/"),
                params: query,
            });
        }
        getSymbolsList().then(function(results) {this.setState({items: results})});
    }
    appContent() {
        var appContent = [];
        if (this.state && this.state.path && this.state.path[0] === "list") {
            appContent.push(React.createElement(ListView, {items: this.state.items}));
            if (this.state.params.ticker) {
                appContent.push(React.createElement(StockProfile, {symbol: this.state.params.ticker}));
            }
        }
    }
    render() {
        return React.createElement("div", {className: "app-container"}, this.appContent());
    }
}


class ListView extends React.Component {
    constructor(props) {
        super(props);
    }
    render() {
        return React.createElement("div", {className: "list-view"},
            this.props.items.map(function(item) {
                return React.createElement(ListItem, {ticker: item.ticker});
            })
        );
    }
}


class ListItem extends React.Component {
    constructor(props) {
        super(props);
    }
    openModal() {
        var aTag = document.createElement("a");
        aTag.setAttribute("href", window.location.href);
        hash = a.hash.split("?");
        query = {};
        hash[1].split("&").map(function(pairs) {
            pairs = pairs.split("=");
            query[decodeURIComponent(paris[0])] = decodeURIComponent(pairs[1]);
        });
        query.ticker = this.props.ticker;
        window.location.href = "#/" + hash + "?" + Object.keys(query).map(function(param) {return encodeURIComponent(param) + "=" + encodeURIComponent(query[param])}).join("&");
    }
    render() {
        return React.createElement("div", {
            className: "list-item",
            onClick: this.openModal(),
        }, this.props.ticker);
    }
}
