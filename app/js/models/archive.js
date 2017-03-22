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
        if (!options.duration || !options.calculation || !options.trendRatio) {
            throw "Invalid Own Condition";
        }
        this.duration = options.duration;
        this.calculation = options.calculation;
        this.trendRatio = options.trendRatio;
    }
    testCondition(simulationData) {
        if (this.calculation === "macdLinearRegression") {
            return this.macdLinearRegressionAnalysis(simulationData);
        }
    }
    macdLinearRegressionAnalysis(simulationData) {
        var macdVals, xVals = [], diff = 0, currRatio = null;
        macdVals = simulationData.map(function(pt, i) {
            xVals.push(Number(i));
            return pt.ema12 - pt.ema26 - pt.macd_ema9
        });
        while (xVals.length - diff > 2) {
            const curr = calculateLeastSquaresLinearRegression(xVals.slice(0, xVals.length - diff), macdVals.slice(diff));
            const newRatio = (curr[curr.length-1] - curr[0]) / curr.length;
            if (currRatio === null) {
                currRatio = newRatio
            } else {
                if (newRatio - currRatio < this.trendRatio) {
                    return false;
                }
                currRatio = newRatio;
            }
            diff++;
        }
        return true;
    }
}
