"""
Source - https://www.youtube.com/watch?v=p_rmpE0XwCc

"""
from sklearn.datasets import load_wine
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

if __name__ == '__main__':

    wines = load_wine()

    #print(wines['DESCR'])

    X, y = wines['data'], wines['target']

    #%matplotlib inline

    plt.hist(y)

    scaler = StandardScaler()

    svm = SVC(C=1e-1, kernel='linear', degree=4)

    X = scaler.fit(X).transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
    y_pred = svm.fit(X_train, y_train).predict(X_test)

    print(f""" {

    classification_report(y_pred, y_test)}

    Confusion matrix:
    {confusion_matrix(y_pred, y_test)}

    Number of support vectors per class: {svm.n_support_}

    """)