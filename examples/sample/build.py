cc = use('gcc', '-c')
ln = use('gcc')

obj1_rule = rule(r'.*\.cc', cc)
obj2_rule = rule(r'.*\.cpp', cc)
prog_rule = rule(obj1_rule + obj2_rule, ln, output='program')
