from django.test.testcases import TestCase
from notes.models import Document, Tag, Tagmap
from notes.forms import AddTagForm

import networkx as nx
import plotly as py
import plotly.graph_objs as go


class NetworkXTests(TestCase):

    def test_make_networkx_do_something(self):
        """
        Check out: https://stackoverflow.com/questions/50078361/customizing-a-networkx-graph-or-scatter-with-python-plotly
        and: https://plot.ly/python/network-graphs/
        and: https://networkx.github.io/documentation/stable/tutorial.html
        :return:
        """
        graph = nx.Graph()
        #node1 = (1, {'pos': (1, 1)})
        #node2 = (2, {'pos': (2, 2)})
        #node3 = (3, {'pos': (3, 3)})
        #graph.add_nodes_from([node1, node2, node3])

        graph.add_nodes_from([1, 2, 3, 'TestNode'])
        pos = nx.spring_layout(graph)  # Gives the node coordinates????
        print('pos:', pos)
        for node in graph.nodes():
        #for node in list(graph.nodes.data()):
            graph.nodes[node]['pos'] = pos[node]
            #node['pos'] = pos[node]

        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            marker=dict(
                size=16
            )

        )

        for node in graph.nodes():
            print('node:', node)
            x, y = graph.nodes[node]['pos']
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['text'] += tuple([str(node)])

        graph.add_edge(1, 2)
        graph.add_edge(1, 3)

        edge_trace = go.Scatter(
            x=[],
            y=[],
            mode='lines'
        )

        for edge in graph.edges():
            print('edge:', edge)
            print('graph.node[edge[0]]:', graph.nodes[edge[0]])
            print('graph.node[edge[1]]:', graph.nodes[edge[1]])
            x0, y0 = graph.nodes[edge[0]]['pos']
            x1, y1 = graph.nodes[edge[1]]['pos']
            #edge_trace['x'] += tuple([x0, x1, None])
            edge_trace['x'] += tuple([x0, x1])
            #edge_trace['y'] += tuple([y0, y1, None])
            edge_trace['y'] += tuple([y0, y1])

        print('node_trace:', node_trace)
        print('edge_trace:', edge_trace)

        # Generate the plot of the network.
        self.plot_network(node_trace, edge_trace)

    def plot_network(self, nodes, edges):
        """ Plots the edges and nodes in the network. """

        fig = go.Figure(data=[edges, nodes],
                        layout=go.Layout(
                            title='<br>Network graph made with Python</br>',
                            titlefont=dict(size=16),
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            annotations=[dict(
                                text="Test Text",
                                showarrow=False,
                                xref="paper", yref="paper",
                                x=0.005, y=-0.002)],
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

        py.offline.plot(fig, filename=r'./notes/tests/test-plot1.html', auto_open=False)