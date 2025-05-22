# food_server.py
from flask import Flask, request, jsonify
import torch
import numpy as np
from collections import OrderedDict
import os

from food_model import FoodPreferenceModel, weights_from_json_serializable, weights_to_json_serializable
import federated_config as config

app = Flask(__name__)

# Server state
global_model_weights = None # Will store the state_dict
client_updates = [] # List to store (weights_state_dict, data_size) from clients for the current round
connected_clients_this_round = set()

def save_global_model_to_disk():
    if global_model_weights:
        try:
            torch.save(global_model_weights, config.GLOBAL_MODEL_SAVE_PATH)
            print(f"Server: Global model saved to {config.GLOBAL_MODEL_SAVE_PATH}")
        except Exception as e:
            print(f"Server: Error saving global model: {e}")

def load_global_model_from_disk():
    global global_model_weights
    if os.path.exists(config.GLOBAL_MODEL_SAVE_PATH):
        try:
            # Ensure INPUT_DIM is known before trying to load a model that depends on it.
            # For state_dict, it's less critical at load time, but good practice for model instantiation.
            # If INPUT_DIM is -1, it means no client has set it yet (e.g. server starts fresh).
            # The server doesn't *need* to instantiate the model to store/serve state_dicts.
            if config.INPUT_DIM == -1:
                 print("Server: INPUT_DIM not set. Model structure for loading might be unknown. Loading state_dict directly.")

            global_model_weights = torch.load(config.GLOBAL_MODEL_SAVE_PATH)
            print(f"Server: Global model loaded from {config.GLOBAL_MODEL_SAVE_PATH}")
            # If we wanted to instantiate the model on server:
            # server_model_instance = FoodPreferenceModel(input_dim=config.INPUT_DIM) # Requires INPUT_DIM
            # server_model_instance.load_state_dict(global_model_weights)
            # print("Server: Global model loaded and instantiated.")
        except Exception as e:
            print(f"Server: Error loading global model: {e}. Starting with no pre-loaded model.")
            global_model_weights = None # Reset if loading failed
    else:
        print("Server: No pre-saved global model found. Starting fresh.")


@app.route('/get_global_model', methods=['GET'])
def get_global_model_route():
    if global_model_weights:
        serializable_weights = weights_to_json_serializable(global_model_weights)
        return jsonify({'model_weights': serializable_weights})
    else:
        return jsonify({'model_weights': None, 'message': 'Global model not initialized yet or failed to load.'})


@app.route('/submit_update', methods=['POST'])
def submit_update():
    data = request.get_json()
    client_id = data['client_id']
    
    if client_id in connected_clients_this_round:
        return jsonify({'status': 'error', 'message': f'Client {client_id} already submitted for this round.'}), 400

    try:
        weights_serializable = data['model_weights']
        client_model_weights = weights_from_json_serializable(weights_serializable)
        data_size = data['data_size']
        
        client_updates.append({'weights': client_model_weights, 'size': data_size})
        connected_clients_this_round.add(client_id)
        
        print(f"Server: Received update from {client_id}. Total updates this round: {len(client_updates)}/{config.NUM_USERS}")

        if len(client_updates) >= config.NUM_USERS:
            aggregate_updates()
            save_global_model_to_disk() # Save after aggregation
            client_updates.clear()
            connected_clients_this_round.clear()
            print("Server: Aggregation complete. Ready for next round.")
            
        return jsonify({'status': 'success', 'message': 'Update received'})
    except Exception as e:
        print(f"Server: Error processing update from {client_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


def aggregate_updates():
    global global_model_weights
    if not client_updates:
        print("Server: No updates to aggregate.")
        return

    total_data_size = sum(update['size'] for update in client_updates)
    if total_data_size == 0:
        print("Server: Total data size is zero, cannot aggregate.")
        return

    first_client_weights = client_updates[0]['weights']
    aggregated_weights = OrderedDict()
    for key in first_client_weights.keys():
        aggregated_weights[key] = torch.zeros_like(first_client_weights[key], dtype=torch.float32)

    for update in client_updates:
        client_w = update['weights']
        weighting_factor = update['size'] / total_data_size
        for key in aggregated_weights.keys():
            if key in client_w:
                 aggregated_weights[key] += client_w[key] * weighting_factor
            else:
                print(f"Warning: Key {key} not found in update from a client during aggregation.")

    global_model_weights = aggregated_weights
    print("Server: Global model updated via Federated Averaging.")


if __name__ == '__main__':
    load_global_model_from_disk() # Load model at startup
    print(f"Starting Federated Learning Server on http://{config.SERVER_HOST}:{config.SERVER_PORT}")
    print(f"Expecting updates from {config.NUM_USERS} clients per round.")
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=False)