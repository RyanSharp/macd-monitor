class StockProfile extends React.Component {
    constructor(props) {
        super(props);
    }
    drawPriceChart() {
        var context, data;
        context = this.refs.priceChart.getContext("2d");
        data = this.state.archive.map(function(pt, i) {return {x: pt.date, y: pt.price}});
        console.log(data);
        this.priceChart = new Chart(context, {
            type: "line",
            data: data,
        });
    }
    drawMacdChart() {
        var context;
        context = this.refs.macdChart.getContext("2d");
        this.macdChart = new Chart(context, {
            type: "bar",
            data: this.state.archive.map(function(pt) {return pt.macd_ema9 ? pt.ema12 - pt.ema26 - pt.macd_ema9 : 0}),
        });
    }
    componentDidMount() {
        getFullSymbolArchive(this.props.symbol).then(function(archive) {
            this.setState({archive: archive}, function() {
                this.drawPriceChart();
                this.drawMacdChart();
            }.bind(this));
        }.bind(this))
    }
    render() {
        return React.createElement("div", {className: "stock-profile"},
            React.createElement("canvas", {className: "stock-profile-chart", ref: "priceChart"}),
            React.createElement("canvas", {className: "stock-profile-chart", ref: "macdChart"})
        );
    }
}
