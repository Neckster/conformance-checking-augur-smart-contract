import os
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.petri.exporter import exporter as pnml_exporter
from pm4py.visualization.petrinet import visualizer as pn_visualizer

log = xes_importer.apply(os.path.join("logs", "log_augur_preprocessed.xes"))

net, initial_marking, final_marking = inductive_miner.apply(log)

pnml_exporter.apply(
    net,
    initial_marking,
    os.path.join("petri", "augur_preprocessed_discovered_petri.pnml"),
    final_marking=final_marking
)

parameters = {pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "svg"}
gviz = pn_visualizer.apply(net, initial_marking, final_marking, parameters=parameters)
pn_visualizer.save(gviz, os.path.join("img", "augur_preprocessed_discovered_petri.svg"),)
