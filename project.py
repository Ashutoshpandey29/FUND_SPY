import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

# Load the dataset
df = pd.read_csv('transaction_dataset.csv')

# Function to build a graph from the transactions
def build_graph(df):
    graph = defaultdict(list)
    for index, row in df.iterrows():
        graph[row['Sender']].append((row['Recipient'], row['Transaction ID'], row['Date'], row['Amount']))
    return graph

# DFS function to detect cycles
def dfs(node, graph, visited, stack, start_node, path):
    visited[node] = True
    stack[node] = True
    path.append(node)

    for neighbor, transaction_id, date, amount in graph[node]:
        if not visited[neighbor]:
            if dfs(neighbor, graph, visited, stack, start_node, path):
                return True
        elif stack[neighbor] and neighbor == start_node:
            path.append(neighbor)
            print("Circular Transaction Sequence: " + " -> ".join(path))
            path.pop()
            return True

    path.pop()
    stack[node] = False
    return False

# Function to find and print all circular transactions
def find_and_print_circular_transactions(df):
    graph = build_graph(df)
    visited = {node: False for node in graph}
    stack = {node: False for node in graph}

    for node in graph:
        if not visited[node]:
            path = []
            dfs(node, graph, visited, stack, node, path)

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
    plt.show()

# Find and print circular transactions
find_and_print_circular_transactions(df)
print()

# Plot sudden spikes
plot_sudden_spikes(df)
