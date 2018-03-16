import unittest

from edictreader.dict import Dict


class Test(unittest.TestCase):
    def test_dict(self):
        with self.assertRaisesRegex(TypeError,
                                    "Can't instantiate abstract class Dict with abstract methods __init__"):
            Dict()


if __name__ == '__main__':
    unittest.main()
