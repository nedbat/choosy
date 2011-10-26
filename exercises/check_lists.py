# test_lists.py

def check(exercise, output, c):

    with c.expect("""You should have a list named "my_list"."""):
        names = [n for n in dir(exercise) if not n.startswith('_')]
        c.test(names, 'You have no variables.')
        if not hasattr(exercise, "my_list"):
            if len(names) > 1:
                c.fail('You have these variables: %s.' % (", ".join(sorted(names)),))
            else:
                c.fail('You have this variable: %s' % names[0])
        c.test(isinstance(exercise.my_list, list), 
            "Your my_list isn't a list, it's a %s" % type(exercise.my_list)
            )

    with c.expect('''"my_list" should have 5 elements, all numbers.'''):
        c.test(len(exercise.my_list) == 5, 'Your "my_list" has %d elements.' % len(exercise.my_list))
        c.test(all(isinstance(x, int) for x in exercise.my_list),
            "Your my_list has some non-number elements."
            )

    with c.expect('''There should be a number smaller than 10.'''):
        c.test(any(x < 10 for x in exercise.my_list))

    with c.expect('''There should be a number greater than 10.'''):
        c.test(any(x > 10 for x in exercise.my_list))
