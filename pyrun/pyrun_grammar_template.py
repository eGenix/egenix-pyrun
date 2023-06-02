""" eGenix PyRun Grammar Data.

    This was generated at the time eGenix PyRun was compiled and
    contains the python_grammar and pattern_grammar pickles as
    generated by the pgen2 parser in lib2to3.

    TODO: This file may no longer needed, after we've completely phased out
    lib2to3 support in PyRun.

"""

### Data

# Python grammar
python_grammar_pickle = (
    #$python_grammar_pickle
    )

# Pattern grammar
pattern_grammar_pickle = (
    #$pattern_grammar_pickle
    )

### Helpers

try:
    # Python 2
    import cPickle as pickle
except ImportError:
    # Python 3
    import pickle

def load_python_grammar():
    return pickle.loads(python_grammar_pickle)

def load_pattern_grammar():
    return pickle.loads(pattern_grammar_pickle)
