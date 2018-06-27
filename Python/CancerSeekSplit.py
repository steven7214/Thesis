#!/usr/bin/env python3

from keras.models import Sequential
from keras.layers import Dense
from keras import regularizers
from sklearn.model_selection import StratifiedKFold
import numpy
import os

numpy.random.seed(7)

#define 10-fold cross validation
kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=7)

#get cancers and normal data set
filename = os.path.join(os.getcwd(), '..', 'Data/CancerSEEK/Cancers/Normal.csv')
normalData = numpy.loadtxt(filename, delimiter=",")
filename = os.path.join(os.getcwd(), '..', 'Data/CancerSEEK/Cancers/Liver.csv')
cancerData = numpy.loadtxt(filename, delimiter=",")
filename = os.path.join(os.getcwd(), '..', 'Data/CancerSEEK/Cancers/Testing.csv')
testData = numpy.loadtxt(filename, delimiter=",")

#split data
normal = [normalData[:, 0:40], normalData[:, 40]]
cancer = [cancerData[:, 0:40], cancerData[:, 40]]
total = [numpy.vstack((normal[0],cancer[0])), numpy.hstack((normal[1],cancer[1]))]
testing = [testData[:, 0:40], testData[:, 40], testData[:, 41]]


#create file to write in
filename = os.path.join(os.getcwd(), '..', 'Data/CancerSEEK/CrossValidation/results.csv')
file = open(filename, 'w')

#update/Parameters
update = [5, 0.0005]
parameters = [[15, 0], [15, 0]]

average = 0
previousAccuracy = 0
optimizeIndex = [0, 0]
optimizeAccuracy = 0
go = True
while go:
    for train, test in kfold.split(total[0], total[1]):
        model = Sequential()
        model.add(Dense(parameters[0][0], input_dim=40, kernel_regularizer=regularizers.l2(parameters[0][1]), activation='relu'))
        model.add(Dense(parameters[1][0], kernel_regularizer=regularizers.l2(parameters[1][1]), activation='relu'))
        #model.add(Dense(parameters[2][0], kernel_regularizer=regularizers.l2(parameters[2][1]), activation='relu'))
        model.add(Dense(1, activation='sigmoid'))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        #class_weight makes false positives less desirable
        model.fit(total[0][train], total[1][train], class_weight={0: 50, 1: 1}, epochs=120, batch_size=32, verbose = 0)

        accuracy = model.evaluate(total[0][train], total[1][train], verbose = 0)
        print("train: " + str(accuracy[1]*100))
        accuracy = model.evaluate(total[0][test], total[1][test], verbose = 0)
        print("total: " + str(accuracy[1]*100))
        print ("parameters ")
        print(parameters)
        accuracy = accuracy[1]*100
        average += accuracy
        #if the accuracy is better than before, update parameters
        if accuracy >= previousAccuracy:
            previousAccuracy = accuracy
            parameters[optimizeIndex[0]][optimizeIndex[1]] += update[optimizeIndex[1]]
        else:
            parameters[optimizeIndex[0]][optimizeIndex[1]] -= update[optimizeIndex[1]]
            accuracy = previousAccuracy
            previousAccuracy = 0
            if optimizeIndex[1] == 1:
                optimizeIndex[1] = 0
                optimizeIndex[0] += 1
            else:
                optimizeIndex[1] += 1
            if optimizeIndex[0] >= 2:
                print("finished")
                print(parameters)
                #if there is improvement within the three, update and keep going
                if accuracy - optimizeAccuracy > 0.1:
                    optimizeAccuracy = accuracy
                    optimizeIndex[0] = 0
                #otherwise, break out of all loops
                else:
                    go = False
                    break
print("optimized: " + "\n" + str(parameters))

model = Sequential()
model.add(Dense(parameters[0][0], input_dim=40, kernel_regularizer=regularizers.l2(parameters[0][1]), activation='relu'))
model.add(Dense(parameters[1][0], kernel_regularizer=regularizers.l2(parameters[1][1]), activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(total[0], total[1], class_weight={0: 10, 1: 1}, epochs=120, batch_size=32, verbose = 0)
print(model.evaluate(total[0], total[1], verbose = 0)[1]*100)
print(model.evaluate(testing[0], testing[1], verbose = 0)[1]*100)
#calculate prediction
predictions = model.predict(testing[0])
predictions = predictions.tolist()

#round predictions
rounded = []
for prediction in predictions:
    rounded.append(round(prediction[0]))

#add cancer types
types = testing[2]
#add real cancer value
real = testing[1]

#change to add cancer type
falsePositives = 0
for count in range(len(rounded)):
    if (real[count] == 0 and rounded[count] == 1):
        falsePositives += 1
    line = str(real[count]) + "," + str(rounded[count]) + "," + str(types[count])
    file.write(line + "\n")
print(falsePositives)
file.close()
