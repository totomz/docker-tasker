
'''
* Prende in input una funzione che genera i comandi (producer) ed una funzione che parsa i risultati parziali (reducer)
* init() => crea 2 code su SQS, una lotta di istanze spot, ci installa docker e ci fa pull delle immagini
* genera i comandi e li scrive in una coda
* polla la coda con i risultati e scarica il reducer
'''


class Master:

    def __init__(self, supplier={}, reducer={}, terminate= lambda x:x):
        self.supplier = supplier
        self.reducer = reducer
        self.terminate = terminate

    def start(self):
        print("Ciao bello")

        # Push the task in the queue
        results = list()
        for value in self.supplier():
            print("Generated {}".format(value))
            results.append(value + 500)

        # Collect the results.
        # For how long?
        # Like, wiat for 6 empty messages from SQS
        accumulator = list()
        for result in results:
            self.reducer(result, accumulator)

        self.terminate(accumulator)


def supply():
    n = 1
    while n < 100:
        yield n
        n += 1


def reduce(value, accumulator):
    print("--> {} [{}]".format(value, accumulator))
    accumulator.append(value)


def termination(values):
    print(values)


if __name__ == '__main__':
    master = Master(supplier=supply, reducer=reduce)
    master.start()
    print("### DONE ###")


