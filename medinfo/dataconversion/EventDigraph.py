"""
EventDigraph.py
Class for constructing, manipulating, and analyzing a series of events as a
Directed Graph. Note that the digraph is NOT guaranteed to be acyclic, though
may be - it's up to the caller to enforce that constraint.

e = EventDigraph(events)
"""

import igraph as ig
import networkx as nx
import matplotlib.pyplot as plt

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
        self.model = "igraph"

        if self.model == "networkx":
            self._dg = nx.DiGraph()
        elif self.model == "igraph":
            self._dg = ig.Graph(directed=True)
            self.vertexLabelToId = dict()
            # self.nodes = [(v['name']) for v in self._dg.vs]

        self._addNodesAndEdges(events)

    def nodes(self):
        if self.model == "networkx":
            return self._dg.nodes.items()
        elif self.model == "igraph":
            nodes = list()
            for v in self._dg.vs:
                node = (v['name'], {key: val for (key, val) in v.attributes().iteritems() if key != 'name'})
                nodes.append(node)
            return nodes

    def edges(self):
        if self.model == "networkx":
            return self._dg.edges.items()
        elif self.model == "igraph":
            edges = list()
            for e in self._dg.es:
                sourceLabel = self._dg.vs[e.source]['name']
                destLabel = self._dg.vs[e.target]['name']
                edge = ((sourceLabel, destLabel), {key: val for (key, val) in e.attributes().iteritems() if key != 'name'})
                edges.append(edge)
            return edges

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
            if self.model == "networkx":
                if self._dg.nodes.get(destEventId):
                    # Seen this event before, so just increment count.
                    self._dg.nodes[destEventId]['count'] += 1
                else:
                    # Never seen this event before, so create new node.
                    self._dg.add_node(destEventId, count=1)
            elif self.model == "igraph":
                if destEventId in self.vertexLabelToId:
                    # Seen this even before, so just increment count.
                    vertexId = self.vertexLabelToId[destEventId]
                    self._dg.vs[vertexId]['count'] += 1
                else:
                    # Never seen this event before, so create new vertex.
                    self._dg.add_vertex(destEventId)
                    vertexId = self._dg.vs.find(destEventId).index
                    self._dg.vs[vertexId]['count'] = 1
                    self.vertexLabelToId.update( { destEventId : vertexId } )

            # If this is the start of a new sequence, set sequence label,
            # then continue because there's no edge to be made.
            if sequenceId != currentSequenceId:
                currentSequenceId = sequenceId
            else:
                # Update edge transition count.
                # Destination node is not new, but edge might be new.
                if self.model == "networkx":
                    if destEventId in self._dg.successors(sourceEventId):
                        # Seen this transition before, so just increment count.
                        self._dg.edges[sourceEventId, destEventId]['count'] += 1
                    else:
                        # Never seen transition, so create new edge.
                        self._dg.add_edge(sourceEventId, destEventId, count=1)
                elif self.model == "igraph":
                    sourceVertex = self.vertexLabelToId[sourceEventId]
                    destVertex = self.vertexLabelToId[destEventId]
                    if self._dg.are_connected(sourceVertex, destVertex):
                        # Seen this transition before, so just increment count.
                        self._dg.es.find(_source=sourceVertex, _target=destVertex)['count'] += 1
                    else:
                        # Never seen transition, so create new edge.
                        self._dg.add_edge(sourceVertex, destVertex, count=1)

            # Update sourceEventId.
            sourceEventId = event[2]

    def draw(self, outFilePath):
        # Set node_size to event frequency.
        if self.model == "networkx":
            nodeSizes = [self._dg.nodes[node]['count'] for node in self._dg.nodes()]
            edgeWeights = [self._dg.edges[edge]['count'] for edge in self._dg.edges()]
            nx.draw_networkx(self._dg, node_size=nodeSizes, width=edgeWeights)
            plt.savefig(outFilePath)
        elif self.model == "igraph":
            style = {}
            style['vertex_label'] = self._dg.vs['name']
            style['vertex_size'] = self._dg.vs['count']
            style['edge_width'] = self._dg.es['count']
            style['margin'] = 20
            ig.plot(self._dg, outFilePath, **style)

    def processEvents(self, dbCursor):
        pass


if __name__ == "main":
    pass
