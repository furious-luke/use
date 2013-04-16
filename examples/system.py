ipt, gcc, mpi = install('iptables', 'gcc', 'openmpi')

                    CompoundBuilder(search, install, download)
Package('iptables')                  ->                        Installation


use(
    'iptables',
    config=[
        File(
            'iptables.conf',
            {
                'blah.blah.0.value': 100,
                'host': 'something',
            }
        ),
    ]
)



gcc = rule('gcc', search + install + download)
mpi = rule('mpi', search + install + download)


gcc = use('gcc')
configure(gcc, )
