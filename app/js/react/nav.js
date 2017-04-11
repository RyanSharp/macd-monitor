class Nav extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            items: [],
        };
    }
    handleHashChange() {
        this.setState(parseHashAndQuery());
    }
    componentDidMount() {
        /*
         * Application is too small to justify using routing framework, simple mechanism
         * for handling state changes using the hash of the URL
         * App state is handled on this react element.
         */
        this.handleHashChange();
        window.onhashchange = this.handleHashChange.bind(this);
        getSymbolsList().then(function(results) {this.setState({items: results})}.bind(this));
        var urlInfo = parseHashAndQuery();
        if (urlInfo.path.length === 0 || urlInfo.path[0] === "") {
            urlInfo.path = ["list"];
            window.location.href = generateUrl(urlInfo.path, urlInfo.params);
        }
    }
    appContent() {
        var appContent = [];
        if (this.state && this.state.path && this.state.path[0] === "list") {
            appContent.push(React.createElement(ListView, {items: this.state.items, key: "main-list-view"}));
            if (this.state.params.ticker) {
                appContent.push(React.createElement(Modal, {content: React.createElement(StockProfile, {symbol: this.state.params.ticker})}));
            }
        }
        return appContent;
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
            this.props.items.map(function(item, i) {
                return React.createElement(ListItem, {ticker: item.ticker, key: "main-list-item-" + i});
            })
        );
    }
}


class ListItem extends React.Component {
    constructor(props) {
        super(props);
    }
    openModal() {
        var urlInfo = parseHashAndQuery();
        urlInfo.params.ticker = this.props.ticker;
        window.location.href = generateUrl(urlInfo.path, urlInfo.params);
    }
    render() {
        return React.createElement("div", {
            className: "list-item",
            onClick: this.openModal.bind(this),
        }, this.props.ticker);
    }
}


class Modal extends React.Component {
    constructor(props) {
        super(props);
    }
    render() {
        return React.createElement("div", {className: "modal-backdrop"},
            React.createElement("div", {className: "modal-container"}, this.props.content)
        );
    }
}
