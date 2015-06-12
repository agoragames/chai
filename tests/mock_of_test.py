'''
Tests for the Chai.mock_of() method
'''

import abc

from six import with_metaclass

from chai import Chai

class ContractMeta(abc.ABCMeta):
    pass


class ABCInterface(with_metaclass(abc.ABCMeta)):
    @abc.abstractmethod
    def do_you_mock_me(self):
        pass

    @abc.abstractmethod
    def some_other_function(self):
        pass


class ContractInterface(with_metaclass(ContractMeta)):

    @abc.abstractmethod
    def do_you_mock_me(self):
        pass


class AClass(ABCInterface):
    def do_you_mock_me(self):
        return True

    def some_other_function(self):
        return False


class ContractClass(ContractInterface):
    def do_you_mock_me(self):
        return 'of course I do'


def a_function(x):
    assert isinstance(x, ABCInterface)
    if x.do_you_mock_me():
        return 'Hooray'
    else:
        return 'Why not?'


def c_function(x):
    assert isinstance(x, ContractInterface)
    if x.do_you_mock_me():
        return 'Hooray'
    else:
        return 'Why not?'


class MockOfTest(Chai):
    def test_assert_is_instance(self):
        # Arrange
        mockable = self.mock_of(ABCInterface)
        self.assertIsInstance(mockable, ABCInterface)

    def test_caller_asserts_pass(self):
        mockable = self.mock_of(ABCInterface)
        self.expect(mockable.do_you_mock_me).returns(True).once()

        result = a_function(mockable)

        self.assertEqual(result, 'Hooray')

    def test_inherited_instancecheck(self):
        mockable = self.mock_of(ContractInterface)
        self.assertIn('__instancecheck__', ContractMeta.__dict__)
        self.expect(mockable.do_you_mock_me).returns(True).once()

        result = c_function(mockable)

        self.assertEqual(result, 'Hooray')

    def test_isinstance_still_works_for_real_instances(self):
        mockable = self.mock_of(ABCInterface)
        a = AClass()
        self.assertIsInstance(a, ABCInterface)

    def test_isinstance_fails_nicely(self):
        mockable = self.mock_of(ABCInterface)
        c = ContractClass()
        self.assertFalse(isinstance(c, ABCInterface))
        self.assertFalse(isinstance(6, ABCInterface))
        self.assertFalse(isinstance([], ABCInterface))

    def tearDown(self):
        Chai.tearDown(self)
        # check tidy up for test_inherited_instancecheck
        assert '__instancecheck__' not in ContractMeta.__dict__
