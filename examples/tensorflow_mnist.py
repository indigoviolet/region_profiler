""" Neural Network with Eager API.
A 2-Hidden Layers Fully Connected Neural Network (a.k.a Multilayer Perceptron)
implementation with TensorFlow's Eager API. This example is using the MNIST database
of handwritten digits (http://yann.lecun.com/exdb/mnist/).
This example is using TensorFlow layers, see 'neural_network_raw' example for
a raw implementation with variables.
Links:
    [MNIST Dataset](http://yann.lecun.com/exdb/mnist/).
Author: Aymeric Damien
Project: https://github.com/aymericdamien/TensorFlow-Examples/
"""
from __future__ import print_function

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

import region_profiler as rp

rp.install()

tf.logging.set_verbosity(tf.logging.ERROR)

# Set Eager API
tf.enable_eager_execution()
tfe = tf.contrib.eager

# Parameters
learning_rate = 0.001
num_steps = 1000
batch_size = 128
display_step = 100

# Network Parameters
n_hidden_1 = 256  # 1st layer number of neurons
n_hidden_2 = 256  # 2nd layer number of neurons
num_input = 784  # MNIST data input (img shape: 28*28)
num_classes = 10  # MNIST total classes (0-9 digits)


# Define the neural network. To use eager API and tf.layers API together,
# we must instantiate a tfe.Network class as follow:
class NeuralNet(tfe.Network):
    def __init__(self):
        # Define each layer
        super(NeuralNet, self).__init__()
        # Hidden fully connected layer with 256 neurons
        self.layer1 = self.track_layer(
            tf.layers.Dense(n_hidden_1, activation=tf.nn.relu))
        # Hidden fully connected layer with 256 neurons
        self.layer2 = self.track_layer(
            tf.layers.Dense(n_hidden_2, activation=tf.nn.relu))
        # Output fully connected layer with a neuron for each class
        self.out_layer = self.track_layer(tf.layers.Dense(num_classes))

    def call(self, x):
        with rp.region('NN', asglobal=True):
            with rp.region('layer 1'):
                x = self.layer1(x)
            with rp.region('layer 2'):
                x = self.layer2(x)
            with rp.region('out layer'):
                x = self.out_layer(x)
            return x


# Cross-Entropy loss function
@rp.func()
def loss_fn(inference_fn, inputs, labels):
    # Using sparse_softmax cross entropy
    return tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(
        logits=inference_fn(inputs), labels=labels))


# Calculate accuracy
@rp.func()
def accuracy_fn(inference_fn, inputs, labels):
    prediction = tf.nn.softmax(inference_fn(inputs))
    correct_pred = tf.equal(tf.argmax(prediction, 1), labels)
    return tf.reduce_mean(tf.cast(correct_pred, tf.float32))


@rp.func()
def fetch_mnist():
    return input_data.read_data_sets("/tmp/data/", one_hot=False)


def main():
    mnist = fetch_mnist()
    # Using TF Dataset to split data into batches
    dataset = tf.data.Dataset.from_tensor_slices(
        (mnist.train.images, mnist.train.labels))
    dataset = dataset.repeat().batch(batch_size).prefetch(batch_size)
    dataset_iter = tfe.Iterator(dataset)

    # Create NN
    neural_net = NeuralNet()

    # SGD Optimizer
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    # Compute gradients
    grad = tfe.implicit_gradients(loss_fn)

    # Training
    average_loss = 0.
    average_acc = 0.
    with rp.region('train'):
        for step in range(num_steps):
            # Iterate through the dataset
            with rp.region('fetch_next'):
                d = dataset_iter.next()
                # Images
                x_batch = d[0]
                # Labels
                y_batch = tf.cast(d[1], dtype=tf.int64)

            with rp.region('forward'):
                # Compute the batch loss
                batch_loss = loss_fn(neural_net, x_batch, y_batch)
                average_loss += batch_loss
                # Compute the batch accuracy
                batch_accuracy = accuracy_fn(neural_net, x_batch, y_batch)
                average_acc += batch_accuracy

            if step == 0:
                # Display the initial cost, before optimizing
                print("Initial loss= {:.9f}".format(average_loss))

            with rp.region('backward'):
                # Update the variables following gradients info
                optimizer.apply_gradients(grad(neural_net, x_batch, y_batch))

            # Display info
            if (step + 1) % display_step == 0 or step == 0:
                if step > 0:
                    average_loss /= display_step
                    average_acc /= display_step
                print("Step:", '%04d' % (step + 1), " loss=",
                      "{:.9f}".format(average_loss), " accuracy=",
                      "{:.4f}".format(average_acc))
                average_loss = 0.
                average_acc = 0.

    # Evaluate model on the test image set
    testX = mnist.test.images
    testY = mnist.test.labels
    with rp.region('test'):
        test_acc = accuracy_fn(neural_net, testX, testY)
    print("Testset Accuracy: {:.4f}".format(test_acc))


if __name__ == '__main__':
    main()
