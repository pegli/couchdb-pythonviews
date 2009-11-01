import os
from datetime import datetime
from couchquery import Database, createdb, deletedb

this_directory = os.path.abspath(os.path.dirname(__file__))

# to_seconds_float from 
# http://stackoverflow.com/questions/1083402/missing-datetime-timedelta-toseconds-float-in-python
def to_seconds_float(timedelta):
    """Calculate floating point representation of combined
    seconds/microseconds attributes in :param:`timedelta`.

    :raise ValueError: If :param:`timedelta.days` is truthy.

        >>> to_seconds_float(datetime.timedelta(seconds=1, milliseconds=500))
        1.5
        >>> too_big = datetime.timedelta(days=1, seconds=12)
        >>> to_seconds_float(too_big) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        ValueError: ('Must not have days', datetime.timedelta(1, 12))
    """
    if timedelta.days:
        raise ValueError('Must not have days', timedelta)
    return timedelta.seconds + timedelta.microseconds / 1E6

class ComparisonTimer(object):
    def __init__(self):
        self.timers = {}
    def __call__(self, name, subname, func):
        starttime = datetime.now()
        result = func()
        endtime = datetime.now()
        self.timers.setdefault(name, {})[subname] = (endtime - starttime)
        return result
        
timer = ComparisonTimer()

def setupdb():
    db = Database('http://localhost:5984/test_pythonviews')
    try:
        deletedb(db)
    except: pass
    createdb(db)
    db.sync_design_doc('pythonView', os.path.join(this_directory, 'design'), language='python')
    db.sync_design_doc('javascriptView', os.path.join(this_directory, 'design'), language='javascript')
    return db

def test_small_docs():
    for count in [10, 100, 1000, 10000, 100000]:
        print 'Testing generation of '+str(count)+' small documents.'
        db = setupdb()
        db.create([{'i':x, 'type':'counting'} for x in range(count)])
        py = timer('smalldoc_gen_'+str(count), 'python', 
                        lambda : db.views.pythonView.byType(limit=1)[0])
        js = timer('smalldoc_gen_'+str(count), 'js', 
                        lambda : db.views.javascriptView.byType(limit=1)[0])
        assert py == js
        pyCount = timer('smalldoc_count_'+str(count), 'python', lambda : db.views.pythonView.count()[0])
        jsCount = timer('smalldoc_count_'+str(count), 'js', lambda : db.views.javascriptView.count()[0])
        assert pyCount == jsCount == count
    deletedb(db)
    
def print_perf():
    for key in sorted(timer.timers.keys()):
        js = timer.timers[key]['js']; py = timer.timers[key]['python']
        if js > py:
            print key, ": Python by :", to_seconds_float( js - py)
        else:
            print key, ": Javascript by : ", to_seconds_float( py - js)

if __name__ == '__main__':
    test_small_docs()
    print_perf()