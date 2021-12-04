import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from yellowbrick.classifier import ClassificationReport
"""
    Dataset description:
        # Attributes for both student-mat.csv (Math course) and student-por.csv (Portuguese language course) datasets:
        
        1 address - student's home address type (binary: 'U' - urban or 'R' - rural)
        2 Pstatus - parent's cohabitation status (binary: 'T' - living together or 'A' - apart)
        3 Medu - mother's education (numeric: 0 - none, 1 - primary education (4th grade), 2 â€“ 5th to 9th grade, 3 â€“ secondary education or 4 â€“ higher education)
        4 Fedu - father's education (numeric: 0 - none, 1 - primary education (4th grade), 2 â€“ 5th to 9th grade, 3 â€“ secondary education or 4 â€“ higher education)
        5 Mjob - mother's job (nominal: 'teacher', 'health' care related, civil 'services' (e.g. administrative or police), 'at_home' or 'other')
        6 Fjob - father's job (nominal: 'teacher', 'health' care related, civil 'services' (e.g. administrative or police), 'at_home' or 'other')
        7 traveltime - home to school travel time (numeric: 1 - <15 min., 2 - 15 to 30 min., 3 - 30 min. to 1 hour, or 4 - >1 hour)
        8 studytime - weekly study time (numeric: 1 - <2 hours, 2 - 2 to 5 hours, 3 - 5 to 10 hours, or 4 - >10 hours)
        9 failures - number of past class failures (numeric: n if 1<=n<3, else 4)
        10 paid - extra paid classes within the course subject (Math or Portuguese) (binary: yes or no)
        11 internet - Internet access at home (binary: yes or no)
        12 romantic - with a romantic relationship (binary: yes or no)
        13 freetime - free time after school (numeric: from 1 - very low to 5 - very high)
        14 goout - going out with friends (numeric: from 1 - very low to 5 - very high)

        15 G3 - final grade (numeric: from 0 to 5, output target)
"""



def student_prediction():
   """
   This function predicts student final grade basing on provided dataset.
   Here we used linear kernel function as it generates best predictions.
   Predictions are printed in readable format
   """

   # reading data from csv file
   df = pd.read_csv("..\\Lab4\\student-por.csv", delimiter=";",  header=0)
   x_norm = ['address', 'Pstatus', 'Medu', 'Fedu', 'Mjob', 'Fjob', 'traveltime', 'studytime', 'failures', 'paid', 'internet', 'romantic', 'freetime', 'goout']
   x_data = df[x_norm]

   # maping string values from data set to numbers
   label_dict = {'U': 0, 'R': 1, 'T': 0, 'A': 1, 'teacher': 0, 'health': 1, 'services': 2, 'at_home': 3, 'other': 4, 'no':0, 'yes':1}
   x_data = x_data.replace(label_dict)
   y = df['G3']

   # Mapping values from range 0..20 to 0..5
   for i in range(0, len(y)):
      old_value = y[i]
      y[i] = int(y[i]/3.5)
      #print(f'Mapped {old_value} -> {y[i]}')
   #print(dict(Counter(y)))

   # Histogram
   plt.hist(y, density=10, bins=20)
   plt.xlabel('Ocena')
   plt.ylabel('Ilość')
   plt.show()

   # ?
   fig = plt.figure(figsize=(10, 10))
   ax = plt.axes(projection="3d")
   ax.scatter3D(df['studytime'], df['traveltime'], df['G3'],
                c=df['goout'], alpha=0.4)
   ax.set_xlabel("x")
   ax.set_ylabel("y")
   ax.set_zlabel("z")
   ax.set_title("Relationship between studytime, studytime, and G3")
   plt.show()

   scaler = StandardScaler()
   # Available kernels: { ‘linear’, ‘poly’, ‘rbf’, ‘sigmoid’, ‘precomputed’ }
   svm = SVC(C=1e-1, kernel='poly', degree=8)

   X = scaler.fit(x_data).transform(x_data)

   X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, shuffle=True)
   y_pred = svm.fit(X_train, y_train).predict(X_test)

   classes = [0, 1, 2, 3, 4, 5]

   model = GaussianNB()
   visualizer = ClassificationReport(model, classes=classes, support=True)

   visualizer.fit(X_train, y_train)  # Fit the visualizer and the model
   visualizer.score(X_test, y_test)  # Evaluate the model on the test data
   visualizer.show()  # Finalize and show the figure

   print(classification_report(y_pred, y_test))
   print('Confusion matrix:')
   print(confusion_matrix(y_pred, y_test))
   print(f'Number of support vectors per class: {svm.n_support_}')