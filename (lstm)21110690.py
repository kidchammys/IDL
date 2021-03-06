# -*- coding: utf-8 -*-
"""(lstm)딥러닝개론_CNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_h4OUrzRX8tcT3doD005e-WBdTGteXMA
"""

import tensorflow as tf
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from tensorflow import keras
import datetime
from sklearn.preprocessing import StandardScaler
import random

from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.callbacks import EarlyStopping

# DATA 불러오기 
right = pd.read_csv('./CHEONGJU.csv', parse_dates=['Date'])

# right1 = 'Cheongju' data 중 random하게 이상 값 5% 뽑기 
right1 = right['Cheongju'].sample(frac=0.05, random_state=42)

# 가우시안 그래프 표현하기 
mu1, sigma1 = 1.0, 0.4
x1 = np.linspace(0, 2, 1000)
y1 = (1 / np.sqrt(2 * np.pi * sigma1 ** 2)) * np.exp(-(x1 - mu1) ** 2 / (2 * sigma1 ** 2))

# 이상데이터 만들기 위한 범위 설정하기 
n = 0
sub = []
for n in range(len(x1)):
    if 1.8 <= x1[n]:
        sub.append(x1[n])

sub = np.round(sub, 3)
# right3 = 뽑은 이상 값에 1.5배 하고, 내림차순으로 sort함 
right3 = right1 * random.choice(sub)
right3 = right3.sort_index(ascending=True)

# right['Cheongju']값들을 right['Anomaly']에 넣기 
right['Anomaly'] = right['Cheongju']
right['Anomaly'] = right['Anomaly'].astype(float)

# index에 맞춰서 원본을 이상 값 변경함 
for b in range(len(right3)):
    for c in range(len(right)):
        if right3.index[b] == right['Cheongju'].index[c]:
            right['Anomaly'][c] = right3.iloc[b]
            right['Label'][c] = 1

Normalization = pd.read_csv('./Normalization.csv')

n = 0
window_size = 12
stride_size = 6

for l1 in range(len(Normalization)):
    stride_size = 6

    z = right['Anomaly'][n:(n + window_size)]

    Normalization['Mean'][l1] = z.mean()
    Normalization['Min'][l1] = z.min()
    Normalization['Max'][l1] = z.max()
    Normalization['Variance'][l1] = z.var()
    Normalization['Median'][l1] = z.median()

    n = n + stride_size
    z = right['Anomaly']

cut = int(len(right) / stride_size)
Normalization = Normalization[0:cut]

print(len(Normalization))

# Standardization 평균 0 / 분산 1
scaler = StandardScaler()
scaler = scaler.fit_transform(Normalization)
scaler = pd.DataFrame(scaler)
scaler = scaler.rename(columns={0: 'Mean', 1: 'Min', 2: 'Max', 3: 'Variance', 4: 'Median', 5: 'Label'})

result = pd.DataFrame(Normalization)  # test_input_data.csv의 총 길이 = 742개
result.to_csv('Normalization_ys.csv', header=True, index=True)

Labeling = pd.read_csv('Normalization_ys.csv', index_col=0)

n = 0
window_size = 12
stride_size = 6

for m in range(int(len(right) / stride_size - 1)):
    stride_size = 6

    z = right['Anomaly'][n:(n + window_size)]
    y = right['Cheongju'][n:(n + window_size)]
    y = y.astype(float)

    for w in range(window_size):

        if y.iloc[w] != z.iloc[w]:
            Labeling['Label'][m] = 1
            break
        else:
            Labeling['Label'][m] = 0
    n = n + stride_size
    z = right['Anomaly']

result = pd.DataFrame(Labeling)  # test_input_data.csv의 총 길이 = @@개
result.to_csv('Input_Data.csv', header=True, index=True)

print(len(Labeling))

# 정상데이터 개수
dd = 0
for cc in range(len(Labeling)):
    if Labeling['Label'].iloc[cc] == 0:
        dd = dd + 1

print(dd)

# 이상데이터 개수
d = 0
for c in range(len(Labeling)):
    if Labeling['Label'].iloc[c] == 1:
        d = d + 1

print(d)

df_data1 = pd.read_csv('./Input_Data.csv', index_col=0)
NumData1 = len(df_data1)
NumTrain1 = np.int(NumData1 * 0.7)
NumTest1 = NumData1 - NumTrain1

x_train1 = df_data1.iloc[0:NumTrain1, 0:5].values
y_train1 = df_data1.iloc[0:NumTrain1, -1].values

x_test1 = df_data1.iloc[NumTrain1:, 0:5].values
y_test1 = df_data1.iloc[NumTrain1:, -1].values

# validation data 생성
x_train1, x_val1, y_train1, y_val1 = train_test_split(x_train1, y_train1, test_size=0.2)

x_train1_lstm = x_train1.reshape((x_train1.shape[0], x_train1.shape[1], 1))
x_val1_lstm = x_val1.reshape((x_val1.shape[0], x_val1.shape[1], 1))

model_lstm1 = Sequential()
model_lstm1.add(LSTM(50, activation='relu', input_shape=(x_train1_lstm.shape[1], x_train1_lstm.shape[2])))
model_lstm1.add(Dense(80, activation="relu"))
model_lstm1.add(Dense(120, activation="relu"))
model_lstm1.add(Dense(120, activation="relu"))
model_lstm1.add(Dense(120, activation="relu"))
model_lstm1.add(Dense(80, activation="relu"))
model_lstm1.add(Dense(50, activation="relu"))
model_lstm1.add(Dense(2, activation="relu"))

opt = keras.optimizers.Adam(learning_rate=0.0001)
model_lstm1.compile(loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                    optimizer=opt, metrics=['accuracy'])
model_lstm1.summary()

log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)
early_stopping_callback = EarlyStopping(monitor='val_loss', patience=50)
lstm_history1 = model_lstm1.fit(x_train1_lstm, y_train1, batch_size=32, epochs=1000,
                                validation_data=(x_val1_lstm, y_val1),
                                callbacks=[tensorboard_callback, early_stopping_callback], verbose=2)

lstm_score1 = model_lstm1.evaluate(x_test1, y_test1, verbose=0)

print("Test1 loss:", lstm_score1[0])
print("Test1 accuracy:", round(lstm_score1[1] * 100, 3))
