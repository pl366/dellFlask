import numpy as np
import pandas as pd
from sklearn.cross_validation import train_test_split
from sklearn import ensemble
from sklearn.externals import joblib

data = pd.read_csv("Complaint_survey_data.csv")
data.tail(5)

train = data[data.columns[0:6]][0:69]
target = data['Final Survey Sentiment '][0:69]


x_train , x_test , y_train , y_test = train_test_split(train,target,test_size = 0.00,random_state =2)

clf = ensemble.GradientBoostingRegressor()

clf.fit(x_train, y_train)

joblib.dump(clf,'trained2.pkl') 
