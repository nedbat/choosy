# test_first.py

def check(exercise, output, c):
    with c.expect("""You should have a variable named "a"."""):
        names = [n for n in dir(exercise) if not n.startswith('_')]
        c.test(names, 'You have no variables.')
        if not hasattr(exercise, "a"):
            if len(names) > 1:
                c.fail('You have these variables: %s.' % (", ".join(sorted(names)),))
            else:
                c.fail('You have this variable: %s' % names[0])

    with c.expect('''"a" should equal 17.'''):
        c.test(exercise.a == 17, 'Your "a" equals %r' % exercise.a)

