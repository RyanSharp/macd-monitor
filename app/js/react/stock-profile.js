class StockProfile extends React.Component {
    constructor(props) {
        super(props);
    }
    drawPriceChart() {
        var context, data;
        context = this.refs.priceChart.getContext("2d");
        data = {labels: [], datasets: [{data: []}]};
        this.state.archive.map(function(pt, i) {
            data.labels.push(pt.date);
            data.datasets[0].data.push(pt.price);
        });
        this.priceChart = new Chart(context, {
            type: "line",
            data: data,
            options: {
                maintainAspectRatio: false,
                responsive: true,
                legend: {
                    display: false
                },
                scales: {
                    xAxes: [{display: false}],
                    yAxes: [{afterFit: function(scaleInstance) {scaleInstance.width = 100}}]
                }
            }
        });
    }
    drawMacdChart() {
        var context, data;
        context = this.refs.macdChart.getContext("2d");
        data = {labels: [], datasets: [{data: []}]};
        this.state.archive.map(function(pt, i) {
            data.labels.push(pt.date);
            data.datasets[0].data.push(pt.macd_ema9 ? pt.ema12 - pt.ema26 - pt.macd_ema9 : 0);
        });
        this.macdChart = new Chart(context, {
            type: "bar",
            data: data,
            options: {
                maintainAspectRatio: false,
                responsive: true,
                legend: {
                    display: false
                },
                scales: {
                    xAxes: [{display: false}],
                    yAxes: [{afterFit: function(scaleInstance) {scaleInstance.width = 100}}]
                }
            }
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
    closeSelf() {
        var urlInfo = parseHashAndQuery(), url;
        delete urlInfo.params.ticker;
        url = generateUrl(urlInfo.path, urlInfo.query);
        window.location.href = url;
    }
    render() {
        return React.createElement("div", {className: "stock-profile"},
            React.createElement("div", {className: "profile-header"}, 
                React.createElement("div", {className: "title"}, "Analysis: " + this.props.symbol),
                React.createElement("div", {className: "header-close"},
                    React.createElement("i", {className: "material-icons", onClick: this.closeSelf.bind(this)}, "close")
                )
            ),
            React.createElement("div", {className: "chart-container"},
                React.createElement("div", {className: "stock-profile-chart"},
                    React.createElement("canvas", {ref: "priceChart"})
                ),
                React.createElement("div", {className: "stock-profile-chart"},
                    React.createElement("canvas", {ref: "macdChart"})
                )
            )
        );
    }
}
