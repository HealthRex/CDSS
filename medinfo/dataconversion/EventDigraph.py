"""
EventDigraph.py
Class for constructing, manipulating, and analyzing a series of events as a
Directed Graph. Note that the digraph is NOT guaranteed to be acyclic, though
may be - it's up to the caller to enforce that constraint.

e = EventDigraph(events)
"""

import networkx as nx

class EventDigraph:
    def __init__(self, events):
        """
        Assume that events is an ordered list of tuples of the following form,
        ordered by sequenceId, eventTime, eventName:
            [
                (sequenceA.id, eventTime, eventA.id)
                (sequenceA.id, eventTime, eventB.id)
                (sequenceA.id, eventTime, eventC.id)
                (sequenceB.id, eventTime, eventC.id)
                (sequenceB.id, eventTime, eventA.id)
                (sequenceB.id, eventTime, eventD.id)
            ]

        That event series will produce the following graph:
            [
                eventA --> eventB (weight: 1)
                eventA --> eventD (weight: 1)
                eventB --> eventC (weight: 1)
                eventC --> eventA (weight: 1)
            ]
        """
        self._dg = nx.DiGraph()
        self.nodes = self._dg.nodes
        self.edges = self._dg.edges

        self._addNodesAndEdges(events)

    def _addNodesAndEdges(self, events):
        # Iterate through events, adding nodes and edges to graph while updating
        # node and edge weights along the way.
        currentSequenceId = None
        sourceEventId = None
        for event in events:
            sequenceId = event[0]
            destEventTime = event[1]
            destEventId = event[2]


            # Update node event count.
            if self._dg.nodes.get(destEventId):
                # Seen this event before, so just increment count.
                self._dg.nodes[destEventId]['count'] += 1
            else:
                # Never seen this even before, so create new node.
                self._dg.add_node(destEventId, count=1)

            # If this is the start of a new sequence, set sequence label,
            # then continue because there's no edge to be made.
            if sequenceId != currentSequenceId:
                currentSequenceId = sequenceId
            else:
                # Update edge transition count.
                # Destination node is not new, but edge might be new.
                if destEventId in self._dg.successors(sourceEventId):
                    # Seen this transition before, so just increment count.
                    self._dg.edges[sourceEventId, destEventId]['count'] += 1
                else:
                    # Never seen transition, so create new edge.
                    self._dg.add_edge(sourceEventId, destEventId, count=1)

            # Update sourceEventId.
            sourceEventId = event[2]


    def processEvents(self, dbCursor):
        pass


if __name__ == "main":
    pass
