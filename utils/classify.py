'''
    Author: Ryan Sharp
    Date: 03/17/2017

    Module for handling linear regression and model fitting of our data
'''
from sklearn import linear_model


def stock_health_linear_regression(health_factors):
    '''
        runs linear regression, and returns health factors as array after
        being fit to the linear regression model
    '''
    x_vals = [[x + 1] for x in xrange(len(health_factors.keys()))]
    y_vals = [health_factors[str(x[0]) + "d"] for x in x_vals]
    regr = linear_model.LinearRegression()
    regr.fit(x_vals, y_vals)
    shaped_y_vals = regr.predict(x_vals)
    return shaped_y_vals
