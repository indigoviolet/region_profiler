.. Region Profiler documentation master file, created by
   sphinx-quickstart on Tue Dec 25 15:45:00 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Region Profiler - handy Python profiler
#######################################

.. image:: https://badge.fury.io/py/region-profiler.svg
    :target: https://badge.fury.io/py/region-profiler
.. image:: https://readthedocs.org/projects/region-profiler/badge/?version=latest
    :target: https://region-profiler.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://travis-ci.com/metopa/region_profiler.svg?branch=master
    :target: https://travis-ci.com/metopa/region_profiler
.. image:: https://codecov.io/gh/metopa/region_profiler/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/metopa/region_profiler


Mark regions using ``with``-statements and decorators.
Time region hierarchy and get detailed console report as well as Chrome Trace log.

Contents
--------

.. toctree::
   :maxdepth: 2

   getting_started
   documentation

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Example
=======

Mark some code regions for profiling::

  import region_profiler as rp                # <<<<<

  class NeuralNet(tfe.Network):
    def __init__(self):
        ...

    def call(self, x):
        with rp.region('NN', asglobal=True):  # <<<<<
            with rp.region('layer 1'):        # <<<<<
                x = self.layer1(x)
            with rp.region('layer 2'):        # <<<<<
                x = self.layer2(x)
            with rp.region('out layer'):      # <<<<<
                x = self.out_layer(x)
            return x

  @rp.func()                                  # <<<<<
  def loss_fn(inference_fn, inputs, labels):
      ...

  @rp.func()                                  # <<<<<
  def accuracy_fn(inference_fn, inputs, labels):
      ...

  with rp.region('train'):                    # <<<<<
      for step in range(num_steps):
          with rp.region('forward'):          # <<<<<
              batch_loss = loss_fn(neural_net, x_batch, y_batch)
              batch_accuracy = accuracy_fn(neural_net, x_batch, y_batch)
          with rp.region('backward'):         # <<<<<
              optimizer.apply_gradients(grad(neural_net, x_batch, y_batch))

Enable profiling by calling :func:`region_profiler.install`::

  if __name__ == '__main__':
      rp.install(chrome_trace_file='trace.json')

See console report and flame graph in Chrome Trace Viewer::

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

.. image:: https://github.com/metopa/region_profiler/raw/master/examples/chrome_tracing.png


Features
========

- **Measure only what you need.** See timing for regions you've marked
  and never waste time on looking at things you're not interested in.
- **Measure third party libraries.** You can mark regions inside arbitrary Python package.
  Just don't forget to rollback changes after you've done :)
  Again, only marked regions count. No need to see timings for unfamiliar library internals.
- **No need to use external tools** (like kernprof) to gather profiling data.
  Profile from within your application and use usual command to run it.
- **Average region overhead is 3-10 us** (Python 3.7, Intel Core i5).
- **Chrome Trace log generation.**
- **Table or CSV report format.**
- **No dependencies.**

Why another Python profiler
===========================

While other profilers often focus
on some particular granularity (e.g. function or single line),
Region Profiler allows user to choose the size of the scope of interest
each time, moving from whole function to a subset of lines to a single iteration.

Region Profiler report
contains information only about user-defined regions --
if we are investigating some complicated framework, we don't need to
time its internals outside of the region that we're interested in.

In contrary to majority of existing profilers,
Region Profiler does not require any special programs/switches
(like kernprof) for application start.
This tool is very useful for investigating bottlenecks
of bigger applications, that has complicated start process
(e.g. distributed NN trainer, that is run on a cluster using MPI).

License
=======
MIT © Viacheslav Kroilov <slavakroilov@gmail.com>

