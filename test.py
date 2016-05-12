from client import Client
from time import time
import timeit
import random
import unittest


class CryptoDatingTest(unittest.TestCase):
    def setUp(self):
        self.possibilities = [(choice_1, choice_2)
                              for choice_1 in (False, True)
                              for choice_2 in (False, True)]

    @classmethod
    def setUpClass(cls):
        cls.epoch = int(time())*1000

    def helper_clients_honest(self, choice_1, choice_2):
        self.__class__.epoch += 1
        print "Testing clients with choices", choice_1, choice_2
        A = Client("A", self.__class__.epoch, 0, 1)
        B = Client("B", self.__class__.epoch, 2, 3)
        self.assertTrue(A.register())
        self.assertTrue(B.register())
        self.assertTrue(A.initiate("B"))
        self.assertTrue(B.initiate("A"))
        self.assertTrue(A.get_key("B"))
        self.assertTrue(B.get_key("A"))
        self.assertTrue(A.send_circuit("B", choice_1))
        self.assertTrue(B.send_circuit("A", choice_2))
        self.assertEqual(A.get_result("B"), choice_1 and choice_2)
        self.assertEqual(B.get_result("A"), choice_1 and choice_2)

    def helper_clients_honest_timer(self, choice_1, choice_2):
        self.__class__.epoch += 1
        A = Client("A", self.__class__.epoch, 0, 1)
        B = Client("B", self.__class__.epoch, 2, 3)
        A.register()
        B.register()
        A.initiate("B")
        B.initiate("A")
        A.get_key("B")
        B.get_key("A")
        A.send_circuit("B", choice_1)
        B.send_circuit("A", choice_2)
        A.get_result("B")
        B.get_result("A")

    def test_clients_honest(self):
        for possibility in self.possibilities:
            self.helper_clients_honest(*possibility)

    @unittest.skip('This delays execution')
    def test_time(self):
        get_rand_arg = lambda : random.choice(self.possibilities)
        full_round = lambda : self.helper_clients_honest_timer(*get_rand_arg())
        print timeit.timeit(full_round, number=1000)/1000., 'seconds to do',\
                'a single run on local network.'

if __name__ == '__main__':
    unittest.main()
