import inspect
import unittest

from mock import call, create_autospec


class CallTest(unittest.TestCase):


    def test_spec_inspect_signature_annotations(self):

        def foo(a: int, b: int=10, *, c:int) -> int:
            return a + b + c

        self.assertEqual(foo(1, 2, c=3), 6)
        mock = create_autospec(foo)
        mock(1, 2, c=3)
        mock(1, c=3)

        self.assertEqual(inspect.getfullargspec(mock), inspect.getfullargspec(foo))
        self.assertEqual(mock.mock_calls, [call(1, 2, c=3), call(1, c=3)])
        self.assertRaises(TypeError, mock, 1)
        self.assertRaises(TypeError, mock, 1, 2, 3, c=4)
