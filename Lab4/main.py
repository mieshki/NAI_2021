"""
Prediction model based on SVM methods

Authors:
Reiter, Aleksander <https://github.com/block439>
Dziadowiec, Mieszko <https://github.com/mieshki>
How to run:
(optional): `pip install -r requirements.txt`
"""

from sklearn.datasets import load_wine
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from student_data import student_prediction

def wine_prediction():
    """
    This function predicts class of wine basing on provided
    :return:
    """
    wines = load_wine()
    print(wines['DESCR'])

    X, y = wines['data'], wines['target']

    plt.hist(y)

    scaler = StandardScaler()

    svm = SVC(C=1e-1, kernel='linear', degree=4)

    X = scaler.fit(X).transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.8)
    y_pred = svm.fit(X_train, y_train).predict(X_test)

    print(f""" 
        {

    classification_report(y_pred, y_test)}

        Confusion matrix:
        {confusion_matrix(y_pred, y_test)}

        Number of support vectors per class: {svm.n_support_}

        """)

if __name__ == '__main__':
    # function call to print wine class prediction
    #wine_prediction()

    # function call to print student grade prediction
    student_prediction()
