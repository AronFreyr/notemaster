import networkx as nx
import plotly as py
import plotly.graph_objs as go

from ..models import Document, Tag, Tagmap


def test_create_graph():

    graph = nx.Graph()

    #doc_list = Document.objects.filter(document_name__contains='Spring')
    doc_list = Document.objects.all()
    #tag_exclusion_list = ['Spring Annotations', 'Programming', 'Java']
    tag_exclusion_list = ['Programming']

    for doc in doc_list:
        graph.add_node('Doc - ' + doc.document_name)
        for tag in doc.get_all_tags():
            if tag.tag_name not in tag_exclusion_list:
                graph.add_node('Tag - ' + tag.tag_name)
                graph.add_edge('Doc - ' + doc.document_name, 'Tag - ' + tag.tag_name)

    pos = nx.spring_layout(graph)  # Gives the node coordinates????
    print('pos:', pos)
    for node in graph.nodes():
        graph.node[node]['pos'] = pos[node]

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        marker=dict(
            size=16,
            color=[]
        )

    )

    for node in graph.nodes():
        print('node:', node)
        x, y = graph.node[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([str(node)])
        if node[:3] == 'Doc':
            node_trace['marker']['color'] += tuple(['blue'])
        elif node[:3] == 'Tag':
            node_trace['marker']['color'] += tuple(['red'])

    edge_trace = go.Scatter(
        x=[],
        y=[],
        mode='lines',
        line=dict(
            width=0.5,
            color='#888'
        )
    )

    for edge in graph.edges():
        print('edge:', edge)
        print('graph.node[edge[0]]:', graph.node[edge[0]])
        print('graph.node[edge[1]]:', graph.node[edge[1]])
        x0, y0 = graph.node[edge[0]]['pos']
        x1, y1 = graph.node[edge[1]]['pos']
        #edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['x'] += tuple([x0, x1])
        #edge_trace['y'] += tuple([y0, y1, None])
        edge_trace['y'] += tuple([y0, y1])

    print('node_trace:', node_trace)
    print('edge_trace:', edge_trace)

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Network graph made with Python',
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

    py.offline.plot(fig, filename=r'./notesfromxml/tests/test-plot2.html', auto_open=False)
