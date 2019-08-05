import networkx as nx
import plotly as py
import plotly.graph_objs as go

from pprint import pprint
from ..models import Document, Tag, Tagmap


def test_create_graph():

    graph = nx.Graph()

    #doc_list = Document.objects.filter(document_name__contains='Rome')
    doc_list = Document.objects.filter(document_name__contains='Spring')
    #doc_list = Document.objects.all()
    #tag_exclusion_list = ['Spring Annotations', 'Programming', 'Java']
    #tag_exclusion_list = ['Programming']
    tag_exclusion_list = []

    for doc in doc_list:
        #graph.add_node('Doc - ' + doc.document_name, type='Doc', name=doc.document_name)
        graph.add_node('Doc - ' + doc.document_name)
        for tag in doc.get_all_tags():
            if tag.tag_name not in tag_exclusion_list:
                if not graph.has_node('Tag - ' + tag.tag_name):
                    #graph.add_node('Tag - ' + tag.tag_name, type='Tag', name=tag.tag_name)
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
    graph_copy = graph.copy(as_view=True)

    for node in graph.nodes():
        print('------')
        print('node', node)
        for x in graph_copy[node]:
            print(x)
        print('------')

    for node in graph.nodes():
        x, y = graph.node[node]['pos']
        #print(graph.node[node]['name'])
        #print(graph.node[node]['type'])

        #print('node:', node)
        #for x in graph_copy.adj[node]:
        #    print(x)
        #print('---------')
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([str(node)])
        #if graph.node[node]['type'] == 'Doc':
        if node[:3] == 'Doc':
            node_trace['marker']['color'] += tuple(['blue'])
        #elif graph.node[node]['type'] == 'Tag':
        elif node[:3] == 'Tag':
            node_trace['marker']['color'] += tuple(['red'])

    edge_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        textposition='bottom right',
        textfont=dict(
            family='sans serif',
            size=9
        ),
        mode='lines+text',
        line=dict(
            width=0.5,
            color='#888'
        )
    )

    for edge in graph.edges():
        print('edge:', edge)
        #print('graph.node[edge[0]]:', graph.node[edge[0]])
        #print('graph.node[edge[1]]:', graph.node[edge[1]])
        #print('--------')
        node1 = graph.node[edge[0]]
        #print(node1)
        node2 = graph.node[edge[1]]
        #print(node2)
        #print(graph.get_edge_data(edge[0], edge[1]))
        #print('--------')

        x0, y0 = graph.node[edge[0]]['pos']
        x1, y1 = graph.node[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1])
        edge_trace['y'] += tuple([y0, y1])
        edge_trace['text'] += tuple([edge])
        #edge_trace['text'] += tuple([str(graph.node[edge[0]]) + str(graph.node[edge[1]])])

    #print('-----------')
    #for edge in graph.edges():
    #    print('edge:', edge)
    #    print('edge[0]:', graph.node[edge[0]])
    #    print('edge[1]:', graph.node[edge[1]])
    #print('-----------')

    #for x in enumerate(edge_trace):
    #    print(x)
    node_list = []
    for i in range(len(node_trace.text)):
        print('x: ' + str(node_trace.x[i]) + ', y: ' + str(node_trace.y[i]) + ', node: ' + node_trace.text[i])
        node_list.append({'name': node_trace.text[i], 'x': node_trace.x[i], 'y': node_trace.y[i]})

    edge_list = []
    print('------------')
    j = 0
    for i in range(len(edge_trace.text)):
        text_split = edge_trace.text[i].split(', ')
        first_node = text_split[0][2:-1]
        second_node = text_split[1][1:-2]
        #print(edge_trace.text[i].split(', ')[0])
        #print('first x:',  edge_trace.x[j+i])
        print('x: ' + str(edge_trace.x[j+i]) + ', y: ' + str(edge_trace.y[j+i]) + ', first node: ' + first_node)
        print('x: ' + str(edge_trace.x[j + i + 1]) + ', y: ' + str(edge_trace.y[j + i + 1]) + ', second node: ' + second_node)
        edge_list.append({'name': first_node, 'x': edge_trace.x[j+i], 'y': edge_trace.y[j+i]})
        edge_list.append({'name': second_node, 'x': edge_trace.x[j + i + 1], 'y': edge_trace.y[j + i + 1]})
        #print('second x:', edge_trace.x[j + i + 1])
        #print('first y:', edge_trace.y[j + i])
        #print('second y:', edge_trace.y[j + i + 1])
        j += 1
    #pprint(edge_trace.x)


    for node in node_list:
        node_name = node['name']
        for edge in edge_list:
            if edge['name'] == node_name:
                bool_x = node['x'] == edge['x']
                bool_y = node['y'] == edge['y']
                print('name:' + node_name + ', x: ' + str(bool_x) + ', y: ' + str(bool_y))

    """
    for x in range(len(graph.nodes())):
        print('----------')
        print('x:', x)
        print('node_trace[x]:', node_trace[x])
        print('edge_trace[x]:', edge_trace[x])
        print('edge_trace["text"][x]:', edge_trace['text'][x])
        print('----------')
    """
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Network graph made with Python',
                        titlefont=dict(size=16),
                        #showlegend=False,
                        showlegend=True,
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
