from flask import Flask, render_template, request, send_file
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import pickle
import io
import os


with open('static/models/model2_smote.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

application = Flask(__name__)

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
import pandas as pd
import matplotlib.pyplot as plt
import io

import pandas as pd
import matplotlib.pyplot as plt
import os


def plot_sudden_spikes(df):
    spikes = []
    users = df['Sender'].unique()
    
    # Ensure Date is in datetime format
    df['Date'] = pd.to_datetime(df['Date'])
    
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

    # Save plot to a file
    plt.savefig('static/transaction_spikes.png')
    plt.close()
    


@application.route('/')
def index():
    return render_template('index.html')

@application.route('/circular')
def circular():
    cycles = find_and_collect_circular_transactions(df)
    return render_template('circular.html', cycles=cycles)

@application.route('/spikes')
def spikes():
    plot_sudden_spikes(df)
    return render_template('transaction.html')

@application.route("/models")
def models():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Directory for CSV files
    csv_dir = os.path.join(current_dir, "static/csv")

    # List of CSV file names
    csv_files = [
        "output2.csv",
        "output3.csv",
        "output4.csv",
        "output5.csv",
    ]

    # Load CSV files into dataframes and sample 20 rows
    tables = []
    for file in csv_files:
        full_path = os.path.join(csv_dir, file)
        print(f"Checking file: {full_path}")
        if os.path.exists(full_path):
            df = pd.read_csv(full_path)
            df_sampled = df.sample(n= 15)
            html_table = df_sampled.to_html(classes="table table-striped", index=False)
            tables.append(html_table)
            
        else:
            tables.append(f"<p>Error: {file} not found.</p>")

    # Render the template with the tables
    return render_template("mlModel.html", tables=tables)


@application.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        df = pd.read_csv(file, header=None)

        features = df.values

        predictions = model.predict(features)

        df['Prediction'] = predictions

        results = df.to_html(classes='table table-striped', index=False).replace('\n', '')

        return render_template('results.html', tables=results)


if __name__ == '__main__':
    application.run(debug=True, port=5000, host='0.0.0.0')
