
import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

st.set_page_config(page_title="Layering of Bank Accounts - Mission 99.1", layout="wide")

@st.cache_data
def load_data():
    accounts = pd.read_csv("data/accounts.csv")
    transactions = pd.read_csv("data/transactions.csv", parse_dates=["timestamp"])
    return accounts, transactions

accounts, transactions = load_data()

st.sidebar.title("Filters")
q = st.sidebar.text_input("Search account id / holder / email / phone")
min_amount = st.sidebar.number_input("Min transaction amount", value=0, step=1000)
only_susp = st.sidebar.checkbox("Show only suspicious chains", value=False)

# Filter transactions
tx = transactions.copy()
if min_amount > 0:
    tx = tx[tx["amount"] >= min_amount]

if q:
    q = q.lower()
    # find matching accounts
    mask = accounts.apply(lambda row: q in str(row["account_id"]).lower() or q in str(row["holder_name"]).lower() or q in str(row["email"]).lower() or q in str(row["phone"]).lower(), axis=1)
    matched = accounts[mask]["account_id"].tolist()
    tx = tx[(tx["src"].isin(matched)) | (tx["dst"].isin(matched))]

if only_susp:
    tx = tx[tx["suspicious"] == 1]

st.title("Layering of Bank Accounts: Visual Explorer")
st.markdown("**Team:** Mission 99.1 | **Hackathon:** SynHack 3.0")

# Build graph
G = nx.DiGraph()
for _, r in accounts.iterrows():
    G.add_node(r["account_id"], label=r["holder_name"], email=r["email"], phone=r["phone"])

for _, r in tx.iterrows():
    G.add_edge(r["src"], r["dst"], amount=r["amount"], suspicious=int(r.get("suspicious",0)))

# If empty, show message
if G.number_of_nodes() == 0 or G.number_of_edges() == 0:
    st.warning("No transactions to display with current filters.")
else:
    pos = nx.spring_layout(G, seed=42, k=0.6)
    edge_x = []
    edge_y = []
    edge_colors = []
    widths = []
    for u,v,data in G.edges(data=True):
        x0,y0 = pos[u]
        x1,y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        if data.get("suspicious",0) == 1:
            edge_colors.append("red")
            widths.append(2.5)
        else:
            edge_colors.append("lightgray")
            widths.append(1)

    node_x = []
    node_y = []
    node_text = []
    for n in G.nodes():
        x,y = pos[n]
        node_x.append(x)
        node_y.append(y)
        d = G.nodes[n]
        node_text.append(f"{n}<br>{d.get('label','')}<br>{d.get('email','')}")

    fig = go.Figure()
    # draw edges (plotly requires separate traces for color control)
    # we'll add one trace per edge segment to control color
    edge_traces = []
    i = 0
    edges = list(G.edges(data=True))
    for idx, (u,v,data) in enumerate(edges):
        x0,y0 = pos[u]
        x1,y1 = pos[v]
        color = "red" if data.get("suspicious",0)==1 else "lightgray"
        width = 2.5 if data.get("suspicious",0)==1 else 1
        fig.add_trace(go.Scatter(x=[x0,x1], y=[y0,y1], mode="lines", line=dict(color=color, width=width), hoverinfo="none"))

    fig.add_trace(go.Scatter(x=node_x, y=node_y, mode="markers+text", text=[n for n in G.nodes()], textposition="top center",
                             marker=dict(size=18, color="blue"), hovertext=node_text, hoverinfo="text"))

    fig.update_layout(showlegend=False, margin=dict(l=20,r=20,t=20,b=20), xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), height=800)

    st.plotly_chart(fig, use_container_width=True)

    # Show suspicious chains table
    suspicious = tx[tx["suspicious"]==1]
    if not suspicious.empty:
        st.markdown("### Suspicious Transactions")
        st.dataframe(suspicious.sort_values("timestamp").reset_index(drop=True))
