class Archive {
    constructor(archive) {
        this.archive = archive;
    }
    setOwnConditions(conditions) {
        this.ownConditions = conditions;
    }
    runSimulation() {
        var transactions, owned;
        transactions = [];
        owned = 0;
        this.archive.slice(110).map(function(pt, i) {
            var buy = this.ownConditions.map(function(condition) {
                var testData = this.archive.slice(110 - condition.duration + i);
            }.bind(this)).reduce(function(prev, curr) {return prev && curr}, true);
            if (buy && owned === 0) {
                owned++;
                transactions.push({
                    action: "buy",
                    price: pt.price,
                    index: Number(i),
                });
            } else if (owned !== 0) {
                owned = 0;
                transactions.push({
                    action: "sell",
                    price: pt.price,
                    index: Number(i),
                });
            }
        }.bind(this));
        return transactions;
    }
}


class OwnCondition {
    constructor(options) {
        if (!options.duration || !options.calculation || !(!options.field && !options.function) || !options.trendRatio) {
            throw "Invalid Own Condition";
        }
        this.duration = options.duration;
        this.calculation = options.calculation;
        this.field = options.field;
        this.function = options.function;
        this.trendRatio = options.trendRatio;
    }
    testCondition(simulationData) {
        
    }
}
