

class Test:
    @property
    def test_prop(self):
        return 5


def main():
    test = Test()
    print(test.test_prop)
    test.test_prop = 10
    print(test.test_prop)
