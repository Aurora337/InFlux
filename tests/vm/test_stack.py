import pytest

from influx.vm.stack import Stack


def test_stack_push_pop():

    stack = Stack()

    stack.push(10)
    stack.push(20)

    assert stack.pop() == 20
    assert stack.pop() == 10


def test_stack_peek():

    stack = Stack()

    stack.push(5)

    assert stack.peek() == 5
    assert stack.size() == 1


def test_stack_clear():

    stack = Stack()

    stack.push(1)
    stack.push(2)

    stack.clear()

    assert stack.size() == 0


def test_stack_underflow():

    stack = Stack()

    with pytest.raises(IndexError):
        stack.pop()


def test_stack_empty_peek():

    stack = Stack()

    with pytest.raises(IndexError):
        stack.peek()