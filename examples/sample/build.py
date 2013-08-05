cc = use('gcc', '-c')
ln = use('gcc')
mpi = use('mpich2')

obj1_rule = rule(r'.*\.cc', cc + mpi)
# obj2_rule = rule(r'.*\.cpp', cc + mpi)
prog1_rule = rule(obj1_rule, ln + mpi)
# prog2_rule = rule(obj1_rule + obj2_rule, ln, targets='program')

# obj3_rule = rule(r'.*\.cc', cc + mpi)
# prog3_rule = rule(obj3_rule, ln + mpi)
