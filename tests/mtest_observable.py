"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
02.08.24, 11:30
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

manual tests for observable
"""

from el.observable import Observable, ComposedObservable


if __name__ == "__main__":
    print("\n\n== Testing Observable == \n\n")

    print("Create empty integer")
    test = Observable(5)
    print("Current value: ", test.value)

    print("Changing value...")
    test.value = 5
    print("Current value: ", test.value)

    print("Adding Observer...")
    test >> (lambda v: print("observer1 got:", v))

    print("Changing value...")
    test.value = 7

    print("Adding Observer...")
    test >> (lambda v: print("observer2 got:", v))

    print("Changing value...")
    test.value = 8

    print("Creating second observable...")
    second = Observable[int](0)

    print("Chaining to first observable...")
    second << test

    print("Adding Observer to second...")
    second >> (lambda v: print("observer3 got:", v))

    print("Changing value...")
    test.value = 9
    print("Current value first: ", test.value)
    print("Current value second: ", test.value)

    print("Changing value to same...")
    test.value = 9

    #print("\n\n== Testing ComposedObservable == \n\n")

    # TODO: fix this
    #print("Creating two sources...")
    #source1 = Observable[int]()
    #source2 = Observable[int]()
    #
    #print("Creating composed Observable...")
    #composed = ComposedObservable(source1, source2)
    #
    #print("Adding Observer to composed...")
    #composed >> (lambda v: print("composed observer got:", v[0].value, v[1].value))
    #    
    #print("Changing value 1...")
    #source1.value = 9
    #print("Changing value 2...")
    #source2.value = 5