import sys
import pandas
import numpy
import sklearn
import keras # keras==2.12.0
#tensorflow == 2.12.0

print('Python: {}'.format(sys.version))
print('Pandas: {}'.format(pandas.__version__))
print('Numpy: {}'.format(numpy.__version__))
print('Sklearn: {}'.format(sklearn.__version__))
print('Keras: {}'.format(keras.__version__))

import numpy as np
import pandas as pd

url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
names = ['n_pregnant', 'glucose_concentration', 'blood_pressure (mm Hg)', 'skin_thickness (mm)', 'serum_insulin (mu U/ml)', 'BMI', 'pedigree_function', 'age', 'class']

df = pd.read_csv(url, names=names)
# 기술 통계 확인
df.describe()

df[df['glucose_concentration'] == 0]

columns = ['glucose_concentration', 'blood_pressure (mm Hg)', 
           'skin_thickness (mm)', 'serum_insulin (mu U/ml)', 'BMI']

for col in columns:
    df[col].replace(0, np.nan, inplace=True)
df.describe()

df.dropna(inplace=True)
df.describe()

# 데이터프레임을 numpy 배열로 변환 
dataset = df.values
print(dataset.shape)

X = dataset[:, 0:8]
Y = dataset[:, 8].astype(int)

print(X.shape)
print(Y.shape)
print(X[:5])
print(Y[:5])

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler().fit(X)

# 훈련 데이터의 변환과 출력
X_standardized = scaler.transform(X)

data = pd.DataFrame(X_standardized)
data.describe()

from sklearn.model_selection import GridSearchCV, KFold
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from keras.optimizers import Adam

def create_model():
     #  케라스 모델 정의 
     model = Sequential()
     model.add(Dense(8, input_dim = 8, 
                    kernel_initializer='normal', activation='relu'))
     model.add(Dense(4, input_dim = 8, 
                    kernel_initializer='normal', activation='relu'))
     model.add(Dense(1, activation='sigmoid'))
 
     # 모델 컴파일 
     adam = Adam(lr = 0.01)
     model.compile(loss = 'binary_crossentropy', 
                  optimizer = adam, metrics = ['accuracy'])
     return model

# 최적 배치 크기와 에포크를 정하기 위한 그리드 탐색
# 랜덤 시드 정의
seed = 6
np.random.seed(seed)

# 모델 정의
def create_model():
    # 케라스 모델 생성
    model = Sequential()
    model.add(Dense(8, input_dim = 8, 
                    kernel_initializer='normal', activation='relu'))
    model.add(Dense(4, input_dim = 8, 
                    kernel_initializer='normal', activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    # 모델 컴파일 
    adam = Adam(lr = 0.01)
    model.compile(loss = 'binary_crossentropy', 
                  optimizer = adam, 
                  metrics = ['accuracy'])
    return model

# 모델 생성
model = KerasClassifier(build_fn = create_model, verbose = 1)

# 그리드 탐색 매개변수 정의 
batch_size = [10, 20, 40]
epochs = [10, 50, 100]

# 그리드 탐색 매개변수를 딕셔너리로 만들기 
param_grid = dict(batch_size=batch_size, epochs=epochs)

# GridSearchCV 빌드와 적합
grid = GridSearchCV(estimator = model, param_grid = param_grid, 
                    cv = KFold(random_state=seed, shuffle=True), 
                    verbose = 10)
grid_results = grid.fit(X_standardized, Y)

# 결과 보고
print("Best: {0}, using {1}".format(grid_results.best_score_, grid_results.best_params_))
means = grid_results.cv_results_['mean_test_score']
stds = grid_results.cv_results_['std_test_score']
params = grid_results.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print('{0} ({1}) with: {2}'.format(mean, stdev, param))

# 최적 배치 크기와 에포크를 정하기 위한 그리드 탐색
# 필요한 패키지 임포트
from keras.layers import Dropout  # 임포트 라인에 추가 

# 랜덤 시드 정의
seed = 6
np.random.seed(seed)

# 모델 정의 
def create_model(learn_rate, dropout_rate): # 학습률과 드롭아웃 비율을 인자로
    # 카라스 모델 생성
    model = Sequential()
    model.add(Dense(8, input_dim = 8, kernel_initializer='normal', activation='relu'))
    model.add(Dropout(dropout_rate))        # 드롭아웃 레이어 추가 
    model.add(Dense(4, input_dim = 8, kernel_initializer='normal', activation='relu'))
    model.add(Dropout(dropout_rate))        # 드롭아웃 레이어 추가   
    model.add(Dense(1, activation='sigmoid'))
    
    # 모델 컴파일 
    adam = Adam(lr = learn_rate)            # 학습률에 대한 변수 
    model.compile(loss = 'binary_crossentropy', optimizer = adam, metrics = ['accuracy'])
    return model
  
# 모델 생성 
model = KerasClassifier(build_fn = create_model, epochs = 50, 
                        batch_size = 10, verbose = 0)
                        

# 그리트 탐색 매개변수 정의
learn_rate = [0.001, 0.01, 0.1]
dropout_rate = [0.0, 0.1, 0.2]

# 그리드 탐색 매개변수를 딕셔너리로 변환 
param_grid = dict(learn_rate=learn_rate, dropout_rate=dropout_rate)

# GridSearchCV 빌드와 적합
grid = GridSearchCV(estimator = model, param_grid = param_grid, 
                    cv = KFold(random_state=seed, shuffle=True), 
                    verbose = 10)
grid_results = grid.fit(X_standardized, Y)

# 결과 보고
print("Best: {0}, using {1}".format(grid_results.best_score_, grid_results.best_params_))
means = grid_results.cv_results_['mean_test_score']
stds = grid_results.cv_results_['std_test_score']
params = grid_results.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print('{0} ({1}) with: {2}'.format(mean, stdev, param))

# 최적 배치 크기와 에포크를 정하기 위한 그리드 탐색
# 필요한 패키지 임포트
from keras.layers import Dropout  # 임포트 라인에 추가 

# 랜덤 시드 정의
seed = 6
np.random.seed(seed)

# 모델 정의 
def create_model(learn_rate, dropout_rate): # 학습률과 드롭아웃 비율을 인자로
    # 카라스 모델 생성
    model = Sequential()
    model.add(Dense(8, input_dim = 8, kernel_initializer='normal', activation='relu'))
    model.add(Dropout(dropout_rate))        # 드롭아웃 레이어 추가 
    model.add(Dense(4, input_dim = 8, kernel_initializer='normal', activation='relu'))
    model.add(Dropout(dropout_rate))        # 드롭아웃 레이어 추가   
    model.add(Dense(1, activation='sigmoid'))
    
    # 모델 컴파일 
    adam = Adam(lr = learn_rate)            # 학습률에 대한 변수 
    model.compile(loss = 'binary_crossentropy', optimizer = adam, metrics = ['accuracy'])
    return model
  
# 모델 생성 
model = KerasClassifier(build_fn = create_model, epochs = 50, 
                        batch_size = 10, verbose = 0)
                        

# 그리트 탐색 매개변수 정의
learn_rate = [0.001, 0.01, 0.1]
dropout_rate = [0.0, 0.1, 0.2]

# 그리드 탐색 매개변수를 딕셔너리로 변환 
param_grid = dict(learn_rate=learn_rate, dropout_rate=dropout_rate)

# GridSearchCV 빌드와 적합
grid = GridSearchCV(estimator = model, param_grid = param_grid, 
                    cv = KFold(random_state=seed, shuffle=True), 
                    verbose = 10)
grid_results = grid.fit(X_standardized, Y)

# 결과 보고
print("Best: {0}, using {1}".format(grid_results.best_score_, grid_results.best_params_))
means = grid_results.cv_results_['mean_test_score']
stds = grid_results.cv_results_['std_test_score']
params = grid_results.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print('{0} ({1}) with: {2}'.format(mean, stdev, param))

# activation, init 그리드 탐색 

# 랜덤 시드 지정
seed = 6
np.random.seed(seed)

# 모델 정의 
def create_model(activation, init):  # 인자 지정 
    # 모델 생성
    model = Sequential()
    model.add(Dense(8, input_dim = 8, kernel_initializer= init, activation= activation))
    model.add(Dense(4, input_dim = 8, kernel_initializer= init, activation= activation))
    model.add(Dense(1, activation='sigmoid'))
    
    # 모델 컴파일 
    adam = Adam(lr = 0.001)   # 학습률을 하드코딩함.
    model.compile(loss = 'binary_crossentropy', optimizer = adam, metrics = ['accuracy'])
    return model

# 모델 생성
model = KerasClassifier(build_fn = create_model, epochs = 100, 
                        batch_size = 20, verbose = 0)

# 그리드 탐색 매개변수 정의 
activation = ['softmax', 'relu', 'tanh', 'linear']
init = ['uniform', 'normal', 'zero']

# 그리드 탐색 매개변수를 딕셔너리로 변환 
param_grid = dict(activation = activation, init = init)

# GridSearchCV 빌드와 적합
grid = GridSearchCV(estimator = model, param_grid = param_grid, 
                    cv = KFold(random_state=seed, shuffle=True), verbose = 10)
grid_results = grid.fit(X_standardized, Y)

# 결과 보고 
print("Best: {0}, using {1}".format(grid_results.best_score_, grid_results.best_params_))
means = grid_results.cv_results_['mean_test_score']
stds = grid_results.cv_results_['std_test_score']
params = grid_results.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print('{0} ({1}) with: {2}'.format(mean, stdev, param))

# 히든 레이어의 뉴런의 최적 개수를 찾기 위한 그리드 탐색 

# 랜덤 시드 설정 
seed = 6
np.random.seed(seed)

# 모델 정의 
def create_model(neuron1, neuron2):
    # 케라스 모델 생성
    model = Sequential()
    model.add(Dense(neuron1, input_dim = 8, 
                    kernel_initializer= 'uniform', 
                    activation= 'linear'))
    model.add(Dense(neuron2, input_dim = neuron1, 
                    kernel_initializer= 'uniform', 
                    activation= 'linear'))
    model.add(Dense(1, activation='sigmoid'))
    
    # 모델 컴파일
    adam = Adam(lr = 0.001)
    model.compile(loss = 'binary_crossentropy', 
                  optimizer = adam, 
                  metrics = ['accuracy'])
    return model

# 모델 생성
model = KerasClassifier(build_fn = create_model, 
                        epochs = 100, batch_size = 20, verbose = 0)

# 그리드 탐색 매개변수 설정 
neuron1 = [4, 8, 16]
neuron2 = [2, 4, 8]

# 그리드 탐색 매개변수를 딕셔너리로 변화 
param_grid = dict(neuron1 = neuron1, neuron2 = neuron2)

# GridSearchCV 빌드와 적합
grid = GridSearchCV(estimator = model, 
                    param_grid = param_grid, 
                    cv = KFold(random_state=seed, shuffle=True), 
                    refit = True, 
                    verbose = 10)
grid_results = grid.fit(X_standardized, Y)

# 결과 보고
print("Best: {0}, using {1}".format(grid_results.best_score_, grid_results.best_params_))
means = grid_results.cv_results_['mean_test_score']
stds = grid_results.cv_results_['std_test_score']
params = grid_results.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print('{0} ({1}) with: {2}'.format(mean, stdev, param))

# 최적 초매개변수를 가지고 예측값 생성
import numpy as np
y_pred = grid.predict(X_standardized)

print(y_pred.shape)

print(y_pred[:5])

from sklearn.metrics import classification_report, accuracy_score
print(accuracy_score(Y, y_pred))
print(classification_report(Y, y_pred))


example = df.iloc[1]
print(example)

prediction = grid.predict(X_standardized[1].reshape(1, -1))
print(prediction)


Name = input("For test, Please enter your name: ")
print("입력값을 모른다면, 위의 예시를 참고하여 입력하세요. 해당 예시의 표본은 고위험군의 당뇨병 환자입니다.")

data = np.array(data).reshape(1, -1)
n_pregnant = float(input("Please enter the number of times pregnant: "))
data.append(n_pregnant)

glucose_concentration = float(input("Please enter glucose concentration: "))
data.append(glucose_concentration)

blood_pressure = float(input("Please enter blood pressure (mm Hg): "))
data.append(blood_pressure)

skin_thickness = float(input("Please enter skin thickness (mm): "))
data.append(skin_thickness)

serum_insulin = float(input("Please enter serum insulin (mu U/ml): "))
data.append(serum_insulin)

BMI = float(input("Please enter BMI: "))
data.append(BMI)

pedigree_function = float(input("Please enter pedigree function: "))
data.append(pedigree_function)

age = float(input("Please enter age: "))
data.append(age)

print("The collected data is:", data)

# 리스트를 numpy 배열로 변환 후 reshape (모델 예측에 맞게 형식 변경)
data = np.array(data).reshape(1, -1)

# 표준화 처리 (X_standardized와 동일하게 해야함)
# 표준화된 데이터로 예측
data_standardized = scaler.transform(data)  # scaler는 X_standardized를 만든 표준화 객체

# 새로운 데이터로 예측 수행
new_prediction = grid.predict(data_standardized)
print(f"Prediction for {Name}: {new_prediction[0]}")

# 예측값에 대한 추가 정보 출력
if new_prediction[0] == 1:
    print(f"{Name}, Holy shit! based on the input, Adam predicts that you are likely tohave diabetes.")
else:
    print(f"{Name}, good for you! based on the input, Adam predicts that you are not likely to have diabetes.")