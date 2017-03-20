function calculateLeastSquaresLinearRegression(x_vals, y_vals) {
    var sum_x = sum_y = sum_xy = sum_xx = x = y = 0;
    for (var i = 0; i < x_vals.length; i++) {
        x = x_vals[i];
        y = y_vals[i];
        sum_x += x;
        sum_y += y;
        sum_xx += x * x;
        sum_xy += x * y;
    }
    var m = ((x_vals.length * sum_xy) - (sum_x * sum_y) / ((x_vals.length * sum_xx) - (sum_x * sum_x)));
    var b = (sum_y / count) - ((m * sum_x) / count);
    return x_vals.map(function(v) {return (v * m) + b});
}