from flask import Flask, render_template, request, send_file
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import io

app = Flask(__name__)

# Load the dataset
df = pd.read_csv('transaction_dataset.csv')

# Function to build a graph from the transactions
def build_graph(df):
    graph = defaultdict(list)
    for index, row in df.iterrows():
        graph[row['Sender']].append((row['Recipient'], row['Transaction ID'], row['Date'], row['Amount']))
    return graph

# DFS function to detect cycles
def dfs(node, graph, visited, stack, start_node, path, cycles):
    visited[node] = True
    stack[node] = True
    path.append(node)

    for neighbor, transaction_id, date, amount in graph[node]:
        if not visited[neighbor]:
            if dfs(neighbor, graph, visited, stack, start_node, path, cycles):
                return True
        elif stack[neighbor] and neighbor == start_node:
            path.append(neighbor)
            cycles.append(" -> ".join(path))
            path.pop()
            return True

    path.pop()
    stack[node] = False
    return False

# Function to find and collect all circular transactions
def find_and_collect_circular_transactions(df):
    graph = build_graph(df)
    visited = {node: False for node in graph}
    stack = {node: False for node in graph}
    cycles = []

    for node in graph:
        if not visited[node]:
            path = []
            dfs(node, graph, visited, stack, node, path, cycles)
    
    return cycles

# Function to detect sudden spikes and plot them
def plot_sudden_spikes(df):
    spikes = []
    users = df['Sender'].unique()
    for user in users:
        user_transactions = df[df['Sender'] == user].sort_values(by='Date')
        amounts = user_transactions['Amount'].values
        for i in range(1, len(amounts)):
            if amounts[i] > 5 * amounts[i - 1]:
                spikes.append(user_transactions.iloc[i])
    
    # Plotting
    plt.figure(figsize=(12, 6))
    for user in users:
        user_transactions = df[df['Sender'] == user].sort_values(by='Date')
        plt.plot(user_transactions['Date'], user_transactions['Amount'], 'g-')

    spike_dates = [spike['Date'] for spike in spikes]
    spike_amounts = [spike['Amount'] for spike in spikes]
    plt.plot(spike_dates, spike_amounts, 'ro', label='Sudden Spikes')

    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.title('Transaction Amounts with Sudden Spikes Highlighted')
    plt.legend()

    # Save plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/circular')
def circular():
    cycles = find_and_collect_circular_transactions(df)
    return render_template('circular.html', cycles=cycles)

@app.route('/spikes')
def spikes():
    buf = plot_sudden_spikes(df)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
