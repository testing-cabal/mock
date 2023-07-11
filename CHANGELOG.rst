5.1.0
-----

- bpo-44185: :func:`unittest.mock.mock_open` will call the :func:`close`
  method of the file handle mock when it is exiting from the context
  manager. Patch by Samet Yaslan.

- gh-94924: :func:`unittest.mock.create_autospec` now properly returns
  coroutine functions compatible with :func:`inspect.iscoroutinefunction`

- bpo-17013: Add ``ThreadingMock`` to :mod:`unittest.mock` that can be used
  to create Mock objects that can wait until they are called. Patch by
  Karthikeyan Singaravelan and Mario Corchero.

- bpo-41768: :mod:`unittest.mock` speccing no longer calls class properties.
  Patch by Melanie Witt.

5.0.2
-----

- gh-102978: Fixes :func:`unittest.mock.patch` not enforcing function
  signatures for methods decorated with ``@classmethod`` or
  ``@staticmethod`` when patch is called with ``autospec=True``.

- gh-103329: Regression tests for the behaviour of
  ``unittest.mock.PropertyMock`` were added.

5.0.1
-----

- gh-100740: Fix ``unittest.mock.Mock`` not respecting the spec for
  attribute names prefixed with ``assert``.

- gh-100690: ``Mock`` objects which are not unsafe will now raise an
  ``AttributeError`` when accessing an attribute that matches the name of an
  assertion but without the prefix ``assert_``, e.g. accessing
  ``called_once`` instead of ``assert_called_once``. This is in addition to
  this already happening for accessing attributes with prefixes ``assert``,
  ``assret``, ``asert``, ``aseert``, and ``assrt``.

- gh-96127: ``inspect.signature`` was raising ``TypeError`` on call with
  mock objects. Now it correctly returns ``(*args, **kwargs)`` as infered
  signature.

5.0.0
-----

- gh-98624: Add a mutex to unittest.mock.NonCallableMock to protect
  concurrent access to mock attributes.

- bpo-43478: Mocks can no longer be used as the specs for other Mocks. As a
  result, an already-mocked object cannot have an attribute mocked using
  `autospec=True` or be the subject of a `create_autospec(...)` call. This
  can uncover bugs in tests since these Mock-derived Mocks will always pass
  certain tests (e.g. isinstance) and builtin assert functions (e.g.
  assert_called_once_with) will unconditionally pass.

- bpo-45156: Fixes infinite loop on :func:`unittest.mock.seal` of mocks
  created by :func:`~unittest.create_autospec`.

- bpo-41403: Make :meth:`mock.patch` raise a :exc:`TypeError` with a
  relevant error message on invalid arg. Previously it allowed a cryptic
  :exc:`AttributeError` to escape.

- gh-91803: Fix an error when using a method of objects mocked with
  :func:`unittest.mock.create_autospec` after it was sealed with
  :func:`unittest.mock.seal` function.

- bpo-41877: AttributeError for suspected misspellings of assertions on
  mocks are now pointing out that the cause are misspelled assertions and
  also what to do if the misspelling is actually an intended attribute name.
  The unittest.mock document is also updated to reflect the current set of
  recognised misspellings.

- bpo-43478: Mocks can no longer be provided as the specs for other Mocks.
  As a result, an already-mocked object cannot be passed to `mock.Mock()`.
  This can uncover bugs in tests since these Mock-derived Mocks will always
  pass certain tests (e.g. isinstance) and builtin assert functions (e.g.
  assert_called_once_with) will unconditionally pass.

- bpo-45010: Remove support of special method ``__div__`` in
  :mod:`unittest.mock`. It is not used in Python 3.

- gh-84753: :func:`inspect.iscoroutinefunction` now properly returns
  ``True`` when an instance of :class:`unittest.mock.AsyncMock` is passed to
  it.  This makes it consistent with behavior of
  :func:`asyncio.iscoroutinefunction`.  Patch by Mehdi ABAAKOUK.

- bpo-46852: Remove the undocumented private ``float.__set_format__()``
  method, previously known as ``float.__setformat__()`` in Python 3.7. Its
  docstring said: "You probably don't want to use this function. It exists
  mainly to be used in Python's test suite." Patch by Victor Stinner.

- gh-98086: Make sure ``patch.dict()`` can be applied on async functions.

- gh-100287: Fix the interaction of :func:`unittest.mock.seal` with
  :class:`unittest.mock.AsyncMock`.

- gh-83076: Instantiation of ``Mock()`` and ``AsyncMock()`` is now 3.8x
  faster.

- bpo-41877: A check is added against misspellings of autospect, auto_spec
  and set_spec being passed as arguments to patch, patch.object and
  create_autospec.

4.0.3
-----

- bpo-42532: Remove unexpected call of ``__bool__`` when passing a
  ``spec_arg`` argument to a Mock.

- bpo-39966: Revert bpo-25597. :class:`unittest.mock.MagicMock` with
  wraps' set uses default return values for magic methods.

- bpo-41877: Mock objects which are not unsafe will now raise an
  AttributeError if an attribute with the prefix asert, aseert, or assrt is
  accessed, in addition to this already happening for the prefixes assert or
  assret.

- bpo-40126: Fixed reverting multiple patches in unittest.mock. Patcher's
  ``__exit__()`` is now never called if its ``__enter__()`` is failed.
  Returning true from ``__exit__()`` silences now the exception.

4.0.2
-----

- bpo-39915: Ensure :attr:`unittest.mock.AsyncMock.await_args_list` has
  call objects in the order of awaited arguments instead of using
  :attr:`unittest.mock.Mock.call_args` which has the last value of the call.
  Patch by Karthikeyan Singaravelan.

4.0.1
-----

- Remove the universal marker from the wheel.

4.0.0
-----

- No Changes from 4.0.0b1.

4.0.0b1
-------

- The release is a fresh cut of cpython's `4a686504`__. All changes to :mod:`mock`
  from that commit and before are included in this release along with the
  subsequent changes listed below.

  __ https://github.com/python/cpython/commit/4a686504eb2bbf69adf78077458508a7ba131667

- bpo-37972: Subscripts to the `unittest.mock.call` objects now receive
  the same chaining mechanism as any other custom attributes, so that the
  following usage no longer raises a `TypeError`:

  call().foo().__getitem__('bar')

  Patch by blhsing

- bpo-38839: Fix some unused functions in tests. Patch by Adam Johnson.

- bpo-39485: Fix a bug in :func:`unittest.mock.create_autospec` that
  would complain about the wrong number of arguments for custom descriptors
  defined in an extension module returning functions.

- bpo-39082: Allow AsyncMock to correctly patch static/class methods

- bpo-38093: Fixes AsyncMock so it doesn't crash when used with
  AsyncContextManagers or AsyncIterators.

- bpo-38859: AsyncMock now returns StopAsyncIteration on the exaustion of
  a side_effects iterable. Since PEP-479 its Impossible to raise a
  StopIteration exception from a coroutine.

- bpo-38163: Child mocks will now detect their type as either synchronous
  or asynchronous, asynchronous child mocks will be AsyncMocks and
  synchronous child mocks will be either MagicMock or Mock (depending on
  their parent type).

- bpo-38473: Use signature from inner mock for autospecced methods
  attached with :func:`unittest.mock.attach_mock`. Patch by Karthikeyan
  Singaravelan.

- bpo-38136: Changes AsyncMock call count and await count to be two
  different counters. Now await count only counts when a coroutine has been
  awaited, not when it has been called, and vice-versa. Update the
  documentation around this.

- bpo-37555: Fix `NonCallableMock._call_matcher` returning tuple instead
  of `_Call` object when `self._spec_signature` exists. Patch by Elizabeth
  Uselton

- bpo-37251: Remove `__code__` check in AsyncMock that incorrectly
  evaluated function specs as async objects but failed to evaluate classes
  with `__await__` but no `__code__` attribute defined as async objects.

- bpo-38669: Raise :exc:`TypeError` when passing target as a string with
  :meth:`unittest.mock.patch.object`.

- bpo-25597: Ensure, if ``wraps`` is supplied to
  :class:`unittest.mock.MagicMock`, it is used to calculate return values
  for the magic methods instead of using the default return values. Patch by
  Karthikeyan Singaravelan.

- bpo-38108: Any synchronous magic methods on an AsyncMock now return a
  MagicMock. Any asynchronous magic methods on a MagicMock now return an
  AsyncMock.

- bpo-21478: Record calls to parent when autospecced object is attached
  to a mock using :func:`unittest.mock.attach_mock`. Patch by Karthikeyan
  Singaravelan.

- bpo-38857: AsyncMock fix for return values that are awaitable types.
  This also covers side_effect iterable values that happend to be awaitable,
  and wraps callables that return an awaitable type. Before these awaitables
  were being awaited instead of being returned as is.

- bpo-38932: Mock fully resets child objects on reset_mock(). Patch by
  Vegard Stikbakke

- bpo-37685: Fixed ``__eq__``, ``__lt__`` etc implementations in some
  classes. They now return :data:`NotImplemented` for unsupported type of
  the other operand. This allows the other operand to play role (for example
  the equality comparison with :data:`~unittest.mock.ANY` will return
  ``True``).

- bpo-37212: :func:`unittest.mock.call` now preserves the order of
  keyword arguments in repr output. Patch by Karthikeyan Singaravelan.

- bpo-37828: Fix default mock name in
  :meth:`unittest.mock.Mock.assert_called` exceptions. Patch by Abraham
  Toriz Cruz.

- bpo-36871: Improve error handling for the assert_has_calls and
  assert_has_awaits methods of mocks. Fixed a bug where any errors
  encountered while binding the expected calls to the mock's spec were
  silently swallowed, leading to misleading error output.

- bpo-21600: Fix :func:`mock.patch.stopall` to stop active patches that
  were created with :func:`mock.patch.dict`.

- bpo-38161: Removes _AwaitEvent from AsyncMock.

- bpo-36871: Ensure method signature is used instead of constructor
  signature of a class while asserting mock object against method calls.
  Patch by Karthikeyan Singaravelan.

3.0.5
-----

- bpo-31855: :func:`unittest.mock.mock_open` results now respects the
  argument of read([size]). Patch contributed by Rémi Lapeyre.

3.0.4
-----

- Include the license, readme and changelog in the source distribution.

3.0.3
-----

- Fixed patching of dictionaries, when specifying the target with a
  unicode on Python 2.

3.0.2
-----

- Add missing ``funcsigs`` dependency on Python 2.

3.0.1
-----

- Fix packaging issue where ``six`` was missed as a dependency.

3.0.0
-----

- bpo-35226: Recursively check arguments when testing for equality of
  :class:`unittest.mock.call` objects and add note that tracking of
  parameters used to create ancestors of mocks in ``mock_calls`` is not
  possible.

- bpo-31177: Fix bug that prevented using :meth:`reset_mock
  <unittest.mock.Mock.reset_mock>` on mock instances with deleted attributes

- bpo-26704: Added test demonstrating double-patching of an instance
  method.  Patch by Anthony Sottile.

- bpo-35500: Write expected and actual call parameters on separate lines
  in :meth:`unittest.mock.Mock.assert_called_with` assertion errors.
  Contributed by Susan Su.

- bpo-35330: When a :class:`Mock` instance was used to wrap an object, if
  `side_effect` is used in one of the mocks of it methods, don't call the
  original implementation and return the result of using the side effect the
  same way that it is done with return_value.

- bpo-30541: Add new function to seal a mock and prevent the
  automatically creation of child mocks. Patch by Mario Corchero.

- bpo-35022: :class:`unittest.mock.MagicMock` now supports the
  ``__fspath__`` method (from :class:`os.PathLike`).

- bpo-33516: :class:`unittest.mock.MagicMock` now supports the
  ``__round__`` magic method.

- bpo-35512: :func:`unittest.mock.patch.dict` used as a decorator with
  string target resolves the target during function call instead of during
  decorator construction. Patch by Karthikeyan Singaravelan.

- bpo-36366: Calling ``stop()`` on an unstarted or stopped
  :func:`unittest.mock.patch` object will now return `None` instead of
  raising :exc:`RuntimeError`, making the method idempotent. Patch
  byKarthikeyan Singaravelan.

- bpo-35357: Internal attributes' names of unittest.mock._Call and
  unittest.mock.MagicProxy (name, parent & from_kall) are now prefixed with
  _mock_ in order to prevent clashes with widely used object attributes.
  Fixed minor typo in test function name.

- bpo-20239: Allow repeated assignment deletion of
  :class:`unittest.mock.Mock` attributes. Patch by Pablo Galindo.

- bpo-35082: Don't return deleted attributes when calling dir on a
  :class:`unittest.mock.Mock`.

- bpo-0: Improved an error message when mock assert_has_calls fails.

- bpo-23078: Add support for :func:`classmethod` and :func:`staticmethod`
  to :func:`unittest.mock.create_autospec`.  Initial patch by Felipe Ochoa.

- bpo-21478: Calls to a child function created with
  :func:`unittest.mock.create_autospec` should propagate to the parent.
  Patch by Karthikeyan Singaravelan.

- bpo-36598: Fix ``isinstance`` check for Mock objects with spec when the
  code is executed under tracing. Patch by Karthikeyan Singaravelan.

- bpo-32933: :func:`unittest.mock.mock_open` now supports iteration over
  the file contents. Patch by Tony Flury.

- bpo-21269: Add ``args`` and ``kwargs`` properties to mock call objects.
  Contributed by Kumar Akshay.

- bpo-17185: Set ``__signature__`` on mock for :mod:`inspect` to get
  signature. Patch by Karthikeyan Singaravelan.

- bpo-35047: ``unittest.mock`` now includes mock calls in exception
  messages if ``assert_not_called``, ``assert_called_once``, or
  ``assert_called_once_with`` fails. Patch by Petter Strandmark.

- bpo-28380: unittest.mock Mock autospec functions now properly support
  assert_called, assert_not_called, and assert_called_once.
  
- bpo-28735: Fixed the comparison of mock.MagickMock with mock.ANY.

- bpo-20804: The unittest.mock.sentinel attributes now preserve their
  identity when they are copied or pickled.

- bpo-28961: Fix unittest.mock._Call helper: don't ignore the name parameter
  anymore. Patch written by Jiajun Huang.

- bpo-26750: unittest.mock.create_autospec() now works properly for
  subclasses of property() and other data descriptors.

- bpo-21271: New keyword only parameters in reset_mock call.

- bpo-26807: mock_open 'files' no longer error on readline at end of file.
  Patch from Yolanda Robla.

- bpo-25195: Fix a regression in mock.MagicMock. _Call is a subclass of
  tuple (changeset 3603bae63c13 only works for classes) so we need to
  implement __ne__ ourselves.  Patch by Andrew Plummer.

2.0.0 and earlier
-----------------

- bpo-26323: Add Mock.assert_called() and Mock.assert_called_once()
  methods to unittest.mock. Patch written by Amit Saha.

- bpo-22138: Fix mock.patch behavior when patching descriptors. Restore
  original values after patching. Patch contributed by Sean McCully.

- bpo-24857: Comparing call_args to a long sequence now correctly returns a
  boolean result instead of raising an exception.  Patch by A Kaptur.

- bpo-23004: mock_open() now reads binary data correctly when the type of
  read_data is bytes.  Initial patch by Aaron Hill.

- bpo-21750: mock_open.read_data can now be read from each instance, as it
  could in Python 3.3.

- bpo-18622: unittest.mock.mock_open().reset_mock would recurse infinitely.
  Patch from Nicola Palumbo and Laurent De Buyst.

- bpo-23661: unittest.mock side_effects can now be exceptions again. This
  was a regression vs Python 3.4. Patch from Ignacio Rossi

- bpo-23310: Fix MagicMock's initializer to work with __methods__, just
  like configure_mock().  Patch by Kasia Jachim.

- bpo-23568: Add rdivmod support to MagicMock() objects.
  Patch by Håkan Lövdahl.

- bpo-23581: Add matmul support to MagicMock. Patch by Håkan Lövdahl.

- bpo-23326: Removed __ne__ implementations.  Since fixing default __ne__
  implementation in bpo-21408 they are redundant. *** NOT BACKPORTED ***

- bpo-21270: We now override tuple methods in mock.call objects so that
  they can be used as normal call attributes.

- bpo-21256: Printout of keyword args should be in deterministic order in
  a mock function call. This will help to write better doctests.

- bpo-21262: New method assert_not_called for Mock.
  It raises AssertionError if the mock has been called.

- bpo-21238: New keyword argument `unsafe` to Mock. It raises
  `AttributeError` incase of an attribute startswith assert or assret.

- bpo-21239: patch.stopall() didn't work deterministically when the same
  name was patched more than once.

- bpo-21222: Passing name keyword argument to mock.create_autospec now
  works.

- bpo-17826: setting an iterable side_effect on a mock function created by
  create_autospec now works. Patch by Kushal Das.

- bpo-17826: setting an iterable side_effect on a mock function created by
  create_autospec now works. Patch by Kushal Das.

- bpo-20968: unittest.mock.MagicMock now supports division.
  Patch by Johannes Baiter.

- bpo-20189: unittest.mock now no longer assumes that any object for
  which it could get an inspect.Signature is a callable written in Python.
  Fix courtesy of Michael Foord.

- bpo-17467: add readline and readlines support to mock_open in
  unittest.mock.

- bpo-17015: When it has a spec, a Mock object now inspects its signature
  when matching calls, so that arguments can be matched positionally or
  by name.

- bpo-15323: improve failure message of Mock.assert_called_once_with

- bpo-14857: fix regression in references to PEP 3135 implicit __class__
  closure variable (Reopens bpo-12370)

- bpo-14295: Add unittest.mock
