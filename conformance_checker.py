import os
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri.importer import importer as pnml_importer
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.algo.conformance.log_skeleton import algorithm as lsk_conformance
from pm4py.algo.conformance.alignments import algorithm as alignments

INF = 9999

log = xes_importer.apply(
    os.path.join("logs", "log_augur_preprocessed.xes")
)

traces_len = len(log)

net, initial_marking, final_marking = pnml_importer.apply(
    os.path.join("petri", "augur_final.pnml")
)

# TOKEN BASE REPLAY
replayed_traces = token_replay.apply(log, net, initial_marking, final_marking)

trace_fitness_sum = 0
for replayed_trace in replayed_traces:

    if not replayed_trace['trace_is_fit']:
        print(f"{replayed_trace}\n")

    trace_fitness_sum += replayed_trace['trace_fitness']

avg_trace_fitness = trace_fitness_sum / len(replayed_traces)

print("\nTOKEN BASE REPLAY -> %f" % avg_trace_fitness)

# LOG SKELETON
skeleton = {
    # ================================================================================================
    # Contains the couples of activities that happen ALWAYS with the same frequency inside a trace.
    'equivalence': {
        ('create market', 'finalize market'),
        ('create market', 'submit initial report'),
    },

    # ================================================================================================
    # Contains the couples of activities (A,B) such that an occurrence of A is ALWAYS followed,
    # somewhen in the future of the trace, by an occurrence of B.
    'always_after': {
        ('create market', 'submit initial report'),
        ('fork market', 'finalize market'),
        ('create dispute', 'contribute to dispute')
    },

    # ================================================================================================
    # Contains the couples of activities (B,A) such that an occurrence of B is ALWAYS preceded,
    # somewhen in the past of the trace, by an occurrence of A.
    'always_before': {
        # Conditional activities in the loop
        ('purchase complete sets', 'create market'),
        ('claim trading proceeds', 'finalize market'),
        ('redeem dispute crowdsourcer', 'create dispute'),
        ('redeem dispute crowdsourcer', 'contribute to dispute'),
        ('redeem as initial reporter', 'submit initial report'),
        ('contribute to dispute', 'create dispute'),
        ('complete dispute', 'contribute to dispute'),
        ('fork market', 'complete dispute')
    },

    # ================================================================================================
    # Contains the couples of activities (A,B) that NEVER happens together in the history of the trace.
    'never_together': {
    },

    # ================================================================================================
    # Contains the list of directly-follows relations of the log.
    'directly_follows': {
    },

    # ================================================================================================
    # Number of possible occurrences per trace.
    'activ_freq': {
        'create market': {1},
        'submit initial report': {1},
        'fork market': {0, 1},
        'finalize market': {1},
        'redeem as initial reporter': {0, 1},

        # Activities in the loop
        'purchase complete sets': range(INF),
        'create dispute': range(INF),
        'contribute to dispute': range(INF),
        'complete dispute': range(INF),
        'claim trading proceeds': range(INF),
        'redeem dispute crowdsourcer': range(INF),
        'transfer market': range(INF),
    }
}

conf_result = lsk_conformance.apply(log, skeleton)

fit_traces = 0
for trace in conf_result:
    fit_traces += trace['is_fit'] * 1
    if not trace['is_fit']:
        print(trace)

fraction_fitness = fit_traces / traces_len

print(
    "\nLOG SKELETON (%d/%d | %d traces incorrect) -> %f" % (
        fit_traces, traces_len, traces_len - fit_traces, fraction_fitness
    )
)

alignment_traces_fitness = 0
aligned_traces = alignments.apply_log(log, net, initial_marking, final_marking)
for aligned_trace in aligned_traces:
    alignment_traces_fitness += aligned_trace['fitness']

print(
    "\nALIGNMENTS -> %f" % (alignment_traces_fitness / traces_len)
)
