import numpy as np
import pandas as pd
from sklearn.cross_validation import train_test_split
from sklearn import ensemble
from sklearn.externals import joblib

data = pd.read_csv("Dell_data.csv")

train = data[data.columns[1:9]][0:299]
target = data['Customer Sentiment'][0:299]


x_train , x_test , y_train , y_test = train_test_split(train , target , test_size = 0.00,random_state =2)

clf = ensemble.GradientBoostingRegressor(n_estimators = 400, max_depth = 5, min_samples_split = 2,
          learning_rate = 0.1, loss = 'ls')

clf.fit(x_train, y_train)

joblib.dump(clf,'trained.pkl') 
