class StockProfile extends React.Component {
    constructor(props) {
        super(props):
    }
    render() {
        return React.createElement("div", {className: "stock-profile"},
            React.createElement("canvas", {className: "stock-profile-chart", ref: "price-chart"}),
            React.createElement("canvas", {className: "stock-profile-chart", ref: "macd-chart"})
        );
    }
}