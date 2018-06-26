#!/usr/bin/env python3

from keras.models import Sequential
from keras.layers import Dense
from keras import regularizers
from sklearn.model_selection import StratifiedKFold
import numpy
import os

numpy.random.seed(7)

#define 10-fold cross validation
kfold = StratifiedKFold(n_splits=10, shuffle=False, random_state=7)
valueList = []
tempList = []


#get normal data set
filename = os.path.join(os.getcwd(), '..', 'Data/CancerSEEK/Cancers2/Normal.csv')
normalData = numpy.loadtxt(filename, delimiter=",")

fileNames = ['Breast', 'Colorectum', 'Liver', 'Lung', 'Ovary', 'Pancreas', 'UpperGI']
cancerData = [[],[],[],[],[],[],[]]
for j in range(7):
    #get cancer data set
    nameOfFile = 'Data/CancerSEEK/Cancers2/' + fileNames[j] + '.csv'
    filename = os.path.join(os.getcwd(), '..', nameOfFile)
    cancerData[j] = numpy.loadtxt(filename, delimiter=",")

    tempList = []
    for trainPositions, testPositions in kfold.split(cancerData[j][:, 0:40], cancerData[j][:, 40]):
        tempList.append(testPositions)
    valueList.append(tempList)

for trainPositions, testPositions in kfold.split(normalData[:, 0:40], normalData[:, 40]):
    tempList.append(testPositions)
valueList.append(tempList)

#create file to write in
filename = os.path.join(os.getcwd(), '..', 'Data/CancerSEEK/CrossValidation/results.csv')
file = open(filename, 'w')
for x in range(7):
    falsePositive = 0
    totalAccuracy = 0
    wrong = 0
    total = 0
    test = []
    train = []
    for y in range(10):
        #split data
        if x == 0:
            train = [cancerData[0][:, 0:40][valueList[0][y]], cancerData[0][:, 40][valueList[0][y]], cancerData[0][:, 41][valueList[0][y]]]
            test = [cancerData[1][:, 0:40][valueList[1][y]], cancerData[1][:, 40][valueList[1][y]], cancerData[1][:, 41][valueList[1][y]]]
        if x == 1:
            test = [cancerData[0][:, 0:40][valueList[0][y]], cancerData[0][:, 40][valueList[0][y]], cancerData[0][:, 41][valueList[0][y]]]
            train = [cancerData[1][:, 0:40][valueList[1][y]], cancerData[1][:, 40][valueList[1][y]], cancerData[1][:, 41][valueList[1][y]]]
        for z in range(5):
            z += 2
            cancer = [cancerData[z][:, 0:40][valueList[z][y]], cancerData[z][:, 40][valueList[z][y]], cancerData[z][:, 41][valueList[z][y]]]
            if z == x:
                train = [cancer[0], cancer[1]]
            else:
                test  = [numpy.vstack((test[0],cancer[0])), numpy.hstack((test[1],cancer[1])), numpy.hstack((test[2],cancer[2]))]
        for s in range(10):
            normal = [normalData[:, 0:40][valueList[7][s]], normalData[:, 40][valueList[7][s]], normalData[:, 41][valueList[7][s]]]
            if not s == y:
                train = [numpy.vstack((train[0],normal[0])), numpy.hstack((train[1],normal[1]))]
            else:
                test = [numpy.vstack((test[0],normal[0])), numpy.hstack((test[1],normal[1])), numpy.hstack((test[2],normal[2]))]

        print(len(train[0]))
        print(len(test[0]))
        model = Sequential()
        model.add(Dense(30, input_dim=40, kernel_regularizer=regularizers.l2(0), activation='relu'))
        model.add(Dense(25, kernel_regularizer=regularizers.l2(0), activation='relu'))
        model.add(Dense(1, activation='sigmoid'))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        #class_weight makes false positives less desirable
        model.fit(train[0], train[1], class_weight={0: 1, 1: 1}, epochs=120, batch_size=32, verbose = 0)

        accuracy = model.evaluate(train[0], train[1], verbose = 0)
        totalAccuracy += accuracy[1]*100

        #calculate prediction
        predictions = model.predict(test[0])
        predictions = predictions.tolist()

        #round predictions
        rounded = []
        for prediction in predictions:
            rounded.append(round(prediction[0]))

        #add cancer types
        types = test[2]
        #print(len(types))
        #print(len(rounded))
        #add real cancer value
        real = test[1]

        #change to add cancer type
        for count in range(len(rounded)):
            #print(types[count])
            if types[count] == (x+1):
                print("yay")
                total += 1
                if rounded[count] == 0:
                    wrong += 1
            if real[count] == 0 and rounded[count] != 0:
                falsePositive += 1
            line = str(real[count]) + "," + str(rounded[count]) + "," + str(types[count])
            file.write(line + "\n")

    accuracy = ((total-wrong)/total)*100
    print(fileNames[x] + "\n")
    print("Average test accuracy: " + str(totalAccuracy/10) + "\n")
    print("Accuracy: " + str(accuracy) + "\n")
    print("False positives: " + str(falsePositive) + "\n\n\n")
    file.write("\n\n\n")
file.close()
