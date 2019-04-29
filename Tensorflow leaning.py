# Dependencies
import tensorflow as tf
import pandas as pd
import numpy as np

import sqlite3
import pandas as pd
# Create your connection.
cnx = sqlite3.connect('/home/wcl-lab/server/MPC-Movments.db')
df = pd.DataFrame(columns=['MO, SP, MV'])
dataset = pd.DataFrame()
for i in range(12,22):
	#print "SELECT MO,SP,MV FROM AIRWASHER WHERE '2018-11-" +str(i)+ " 17:00:00' > DATE and DATE > '2018-11-" +str(i)+ " 06:00:00'"
	df = pd.read_sql_query("SELECT MO,SP,MV FROM AIRWASHER WHERE SP <= 26 and '2018-11-" +str(i)+ "18:00:00' > DATE and DATE > '2018-11-" +str(i)+ " 06:00:00'", cnx)
	#print df
	dataset = dataset.append(df, ignore_index=True)
print (dataset.size)/3
#print dataset
#dataset.append(df)
X_size = 3
values = list(dataset.columns.values)
X = dataset[values[0:X_size]]
X = np.array(X, dtype='float32')
#print X
dataset = pd.get_dummies(dataset, columns=['MV']) # One Hot Encoding
values = list(dataset.columns.values)

y_size = 2
y = dataset[values[-y_size:]]
y = np.array(y, dtype='float32')
#print y
# X_size = 2
# X = dataset[values[0:X_size]]
# X = np.array(X, dtype='float32')
# print X
# Shuffle Data
indices = np.random.choice(len(X), len(X), replace=False)
X_values = X[indices]
y_values = y[indices]

# Creating a Train and a Test Dataset
test_size = 40
X_test = X_values[-test_size:]
X_train = X_values[:-test_size]
y_test = y_values[-test_size:]
y_train = y_values[:-test_size]
#print y_train

# Session
sess = tf.Session()

# Interval / Epochs
interval = 1
epoch = 150

# Initialize placeholders
X_data = tf.placeholder(shape=[None, X_size], dtype=tf.float32)
print X_data
y_target = tf.placeholder(shape=[None, y_size], dtype=tf.float32)
print y_target
# Input neurons : 4
# Hidden neurons : 8
# Output neurons : 3
hidden_layer_nodes = 5
hidden_layer_nodes1 = 6
hidden_layer_nodes2 = 5

# Create variables for Neural Network layers
w1 = tf.Variable(tf.random_normal(shape=[X_size,hidden_layer_nodes])) # Inputs -> Hidden Layer
b1 = tf.Variable(tf.random_normal(shape=[hidden_layer_nodes]))   # First Bias
w2 = tf.Variable(tf.random_normal(shape=[hidden_layer_nodes,hidden_layer_nodes1])) # Hidden layer -> Hidden layer1
b2 = tf.Variable(tf.random_normal(shape=[hidden_layer_nodes1]))   # Second Bias
w3 = tf.Variable(tf.random_normal(shape=[hidden_layer_nodes1,hidden_layer_nodes2])) # Hidden layer1 -> Hidden layer2
b3 = tf.Variable(tf.random_normal(shape=[hidden_layer_nodes2]))   # Second Bias
w4 = tf.Variable(tf.random_normal(shape=[hidden_layer_nodes2,y_size])) # Hidden layer1 -> Outputs
b4 = tf.Variable(tf.random_normal(shape=[y_size]))   # Third Bias

# Operations
hidden_output = tf.nn.relu(tf.add(tf.matmul(X_data, w1), b1))
hidden_output1 = tf.nn.relu(tf.add(tf.matmul(hidden_output, w2), b2))
hidden_output2 = tf.nn.relu(tf.add(tf.matmul(hidden_output1, w3), b3))
final_output = tf.nn.softmax(tf.add(tf.matmul(hidden_output2, w4), b4))

# Cost Function
loss = tf.reduce_mean(-tf.reduce_sum(y_target*tf.log(final_output), axis=1))
# Optimizer
optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001).minimize(loss)

# Initialize variables
init = tf.global_variables_initializer()
sess.run(init)

# Training
print('Training the model...')
for i in range(1, (epoch + 1)):
    sess.run(optimizer, feed_dict={X_data: X_train, y_target: y_train})
    if i % interval == 0:
        print('Epoch', i, '|', 'Loss:', sess.run(loss, feed_dict={X_data: X_train, y_target: y_train}))

# Prediction
for i in range(len(X_test)):
	print('Actual:', y_test[i], 'Predicted:', np.rint(sess.run(final_output, feed_dict={X_data: [X_test[i]]})))
	print X_test[i]
#print('Actual:', [0., 1.], 'Predicted:', np.rint(sess.run(final_output, feed_dict={X_data: [23.11111 31.       1.     ]]})))
	
