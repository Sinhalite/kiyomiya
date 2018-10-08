import pandas as pd
import numpy
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

first_team_table = pd.read_csv('./csv/first_team_data.csv')
farm_table = pd.read_csv('./csv/farm_data.csv')
after3y_table = pd.read_csv('./csv/after3y_data.csv')

table = pd.merge(farm_table, first_team_table, on=['西暦', '背番号', '選手名'], how='outer')
table = pd.merge(table, after3y_table, on=['選手名'], how='outer')

# フェルナンデスは助っ人外国人だが、なぜかルーキーとして扱われているため削除
table.drop(table.index[table['選手名'] == 'フェルナンデス'], inplace=True)

# 大谷は投手の成績が紛れてしまったので、手動で対応

# NaN -> 0
table.fillna(0, inplace=True)

# '-' -> 0
# '∞' -> 0
table.replace('-', 0, inplace=True)
table.replace('∞', 0, inplace=True)

X = table.iloc[:, 3:-7].values
y = table.loc[:, '3年後本塁打'].values
label = table.loc[:, '選手名'].values

r_forest_k = RandomForestRegressor(
  n_estimators = 500,
  criterion = 'mse',
  n_jobs = -1
)
r_forest_k.fit(numpy.array(X), numpy.array(y))

X_train, X_test, y_train, y_test, label_train, label_test = train_test_split(X, y, label, test_size = 0.2)

### テスト用
r_forest = RandomForestRegressor(
  n_estimators = 500,
  criterion = 'mse',
  n_jobs = -1
)
r_forest.fit(X_train, y_train)

y_predict = r_forest.predict(X_test)

for i, y in enumerate(y_predict):
  print(label_test[i], y_test[i], y)

### 精度の確認
R2test = metrics.r2_score(y_test, y_predict)
print(R2test)
###

###

### 清宮の成績予測
import getResult
kiyomiya_first_team = getResult.get_result(1, '', 'f')[0]
kiyomiya_farm = getResult.get_result(2, '', 'f')[1]
kiyomiya_result = [kiyomiya_farm[3:] + kiyomiya_first_team[3:]]

kiyomiya_predict = r_forest_k.predict(kiyomiya_result)
print(kiyomiya_predict)
###

### 重要度の算出
features = r_forest_k.feature_importances_
features_xy = []
for i, feature_label in enumerate(table.iloc[:, 3:-7]):
  features_xy.append([feature_label, features[i]])
  print(f'{feature_label}:{features[i]}')

features_xy = sorted(features_xy, key = lambda x: x[1])
###

### 重要度のグラフ描画
plt.figure()
plt.barh(range(len(features_xy)), [f[1] for f in features_xy])
plt.yticks(range(len(features_xy)), [f[0] for f in features_xy])
plt.tight_layout()
plt.show()
###