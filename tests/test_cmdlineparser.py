
import sys

from unittest import mock

import colored
import pytest

from jobslib.cmdlineparser import argument, ArgumentParser


@pytest.mark.parametrize(
    'args, kwargs, expected',
    [
        ((), {}, ((), {})),
        ((1, 2), {}, ((1, 2), {})),
        ((), {'baz': 1, 'bar': 2}, ((), {'baz': 1, 'bar': 2})),
        ((1, 2), {'baz': 1, 'bar': 2}, ((1, 2), {'baz': 1, 'bar': 2})),
    ]
)
def test_argument(args, kwargs, expected):
    assert argument(*args, **kwargs) == expected


def test_argument_parser():
    parser = ArgumentParser()
    parser.prog = 'foo'
    with mock.patch.object(parser, 'print_help') as m_print_help:
        with mock.patch.object(parser, 'exit') as m_exit:
                parser.error('something is wrong')
    expected_message = (
        '\n' + colored.fg('red') + 'foo: error: something is wrong' +
        colored.attr('reset') + '\n')
    m_print_help.assert_called_once_with(sys.stderr)
    m_exit.assert_called_once_with(2, expected_message)
