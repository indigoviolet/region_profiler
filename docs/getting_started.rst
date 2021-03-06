Getting started
===============


Dependencies
------------

- Python >= 3.4


Installation
------------

You can install Region Profiler using ``pip``::

    pip install region_profiler

or from sources::

    git clone https://github.com/metopa/region_profiler.git
    cd region_profiler
    python setup.py install

Tutorial
--------

The following snippet shows example usage of Region Profiler::

  import numpy as np
  import region_profiler as rp


  @rp.func()  # profile function
  def f():
      with rp.region('init'):  # measure execution time of the next block
          a = np.arange(1000000)
          b = a.copy('')

      with rp.region('loop'):
          for x in rp.iter_proxy([1, 2, 3, 4], 'iter'):
              # measure time to retrieve next element
              a += x

      with rp.region():  # autoname region
          return np.sum(a * b)


  if __name__ == '__main__':
      rp.install()
      f()

Running this script would yield output similar to this::

  name                  total  % of total  count       min   average       max
  -----------------  --------  ----------  -----  --------  --------  --------
  <main>             31.18 ms     100.00%      1  31.18 ms  31.18 ms  31.18 ms
  . f()              31.09 ms      99.73%      1  31.09 ms  31.09 ms  31.09 ms
  . . init           8.329 ms      26.72%      1  8.329 ms  8.329 ms  8.329 ms
  . . f() <e.py:16>  5.079 ms      16.29%      1  5.079 ms  5.079 ms  5.079 ms
  . . loop           3.134 ms      10.05%      1  3.134 ms  3.134 ms  3.134 ms
  . . . iter         4.573 us       0.01%      4    419 ns  1.143 us  1.779 us



Global regions
--------------

Sometimes we are interested in total running time of a region,
regardless of its caller context. In this case we would like to mark
the region as global.

If we want to measure the forward and backward passes of a neural
network, we can declare ``NN`` class like this
(see `tensorflow_mnist.py <https://github.com/metopa/region_profiler/blob/master/examples/tensorflow_mnist.py>`_ for complete code)::

  class NeuralNet(tfe.Network):
      def __init__(self):
          # Define each layer
          ...

      def call(self, x):
          with rp.region('NN'):
              with rp.region('layer 1'):
                  x = self.layer1(x)
              with rp.region('layer 2'):
                  x = self.layer2(x)
              with rp.region('out layer'):
                  x = self.out_layer(x)
              return x

However, when called from different contexts, ``NN`` region timing would add up to a total.
The profiler summary would look like this. Note that ``NN`` region appears 4 times in the summary::

  name                    total  % of total
  -------------------  --------  ----------
  <main>                12.61 s     100.00%
  . train               11.74 s      93.11%
  . . backward          7.236 s      57.38%
  . . . loss_fn()       2.077 s      16.47%
  . . . . NN            1.790 s      14.19%
  . . . . . layer 1     1.064 s       8.43%
  . . . . . layer 2      526 ms       4.17%
  . . . . . out layer  162.5 ms       1.29%
  . . forward           4.230 s      33.53%
  . . . loss_fn()       2.194 s      17.39%
  . . . . NN            1.880 s      14.91%
  . . . . . layer 1     1.187 s       9.41%
  . . . . . layer 2      506 ms       4.01%
  . . . . . out layer  149.4 ms       1.18%
  . . . accuracy_fn()   1.963 s      15.57%
  . . . . NN            1.703 s      13.50%
  . . . . . layer 1     1.033 s       8.19%
  . . . . . layer 2    491.5 ms       3.90%
  . . . . . out layer  141.6 ms       1.12%
  . . fetch_next       235.3 ms       1.87%
  . test               83.14 ms       0.66%
  . . accuracy_fn()    83.12 ms       0.66%
  . . . NN             81.59 ms       0.65%
  . . . . layer 1      59.41 ms       0.47%
  . . . . layer 2      20.01 ms       0.16%
  . . . . out layer    2.089 ms       0.02%

In order to merge these timings, ``NN`` region should be declared as global::

  class NeuralNet(tfe.Network):
      def __init__(self):
          # Define each layer
          ...

      def call(self, x):
          with rp.region('NN', asglobal=True):
              with rp.region('layer 1'):
                  x = self.layer1(x)
              with rp.region('layer 2'):
                  x = self.layer2(x)
              with rp.region('out layer'):
                  x = self.out_layer(x)
              return x

In this case the summary looks like this::

  name                    total  % of total
  -------------------  --------  ----------
  <main>                12.44 s     100.00%
  . train               11.64 s      93.51%
  . . backward          7.229 s      58.10%
  . . . loss_fn()       2.079 s      16.71%
  . . forward           4.142 s      33.29%
  . . . loss_fn()       2.134 s      17.15%
  . . . accuracy_fn()   1.937 s      15.56%
  . . fetch_next       225.2 ms       1.81%
  . NN                  5.389 s      43.32%
  . . layer 1           3.295 s      26.48%
  . . layer 2           1.544 s      12.41%
  . . out layer        444.0 ms       3.57%
  . test               86.71 ms       0.70%
  . . accuracy_fn()    86.70 ms       0.70%


Chrome Trace
------------

Region Profiler may output log suitable for `Chrome Trace Viewer <https://aras-p.info/blog/2017/01/23/Chrome-Tracing-as-Profiler-Frontend/>`_.

In order to enable such logging, just pass log filename to ``install()`` function::

  rp.install(chrome_trace_file='trace.json')

Then you can open the resulting log in `<chrome://tracing>`_
(obviously, you'd need Chrome browser) for viewing Flame graph of your app execution.
The following Flame graph is for `tensorflow_mnist.py <https://github.com/metopa/region_profiler/blob/master/examples/tensorflow_mnist.py>`_ sample program.

.. image:: https://github.com/metopa/region_profiler/raw/master/examples/chrome_tracing.png

