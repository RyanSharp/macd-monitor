class SimulationSettings extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            ownConditions: [],
        }
    }
    render() {
        return React.createElement("div", {className: "simulation-settings"},
            React.createElement("div", {className: "simulation-own-conditions"}),
            React.createElement("div", {className: "add-own-condition"})
        );
    }
}


class OwnConditionSettings extends React.Component {
    constructor(props) {
        super(props);
    }
    render() {
        return React.createElement("div", {className: "own-condition-form"},
            React.createElement("select", {},
                React.createElement("option", {value: "macdLinearRegression"}, "macdLinearRegression")
            )
        )
    }
}
