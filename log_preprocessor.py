import os

from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.log import Trace, EventLog

log = xes_importer.apply(os.path.join('logs', 'log_augur.xes'))

preprocessed_log = EventLog()

for name in log.attributes:
    preprocessed_log.attributes[name] = log.attributes[name]

for trace in log:

    t = Trace()
    for name in trace.attributes:
        t.attributes[name] = trace.attributes[name]

    skip_trace = False
    market_finalized = False

    for event in trace:
        # Prevents traces with overflowed integers
        if event['concept:name'] == 'contribute to dispute':
            if event['amountStaked'] < 0:
                skip_trace = True
                break
        if event['concept:name'] == 'redeem dispute crowdsourcer':
            if event['amountRedeemed'] < 0:
                skip_trace = True
                break
            if event['reportingFeesReceived'] <= 0:
                continue
        if event['concept:name'] == 'submit initial report':
            if event['amountStaked'] < 0:
                skip_trace = True
                break
        if event['concept:name'] == 'redeem as initial reporter':
            if event['amountRedeemed'] < 0:
                skip_trace = True
                break
            if event['reportingFeesReceived'] <= 0:
                continue

        if event['concept:name'] == 'finalize market':
            market_finalized = True

        t.append(event)

    if not market_finalized or skip_trace:
        continue

    preprocessed_log.append(t)

xes_exporter.apply(preprocessed_log, os.path.join('logs', 'log_augur_preprocessed.xes'))
