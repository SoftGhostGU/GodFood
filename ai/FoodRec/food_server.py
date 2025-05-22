# food_server.py
from flask import Flask, request, jsonify
import torch
import numpy as np
from collections import OrderedDict
import os

# Assuming food_model.py and federated_config.py are in the same directory or PYTHONPATH
from food_model import FoodPreferenceModel, weights_from_json_serializable, weights_to_json_serializable
import federated_config as config

app = Flask(__name__)

global_model_weights = None 
client_updates = [] 
connected_clients_this_round = set()
# Lock for thread-safe operations on shared resources if truly concurrent,
# though Flask by default is single-threaded per worker.
# For this simulation with sequential client updates per round, it's less critical.
# from threading import Lock
# aggregation_lock = Lock()

def save_global_model_to_disk():
    if global_model_weights:
        try:
            # Before saving, ensure global_model_weights is a state_dict (OrderedDict of tensors)
            if not isinstance(global_model_weights, OrderedDict) or \
               not all(isinstance(t, torch.Tensor) for t in global_model_weights.values()):
                print("Server: Attempted to save invalid global_model_weights type. Skipping save.")
                return

            torch.save(global_model_weights, config.GLOBAL_MODEL_SAVE_PATH)
            print(f"Server: Global model saved to {config.GLOBAL_MODEL_SAVE_PATH}")
        except Exception as e:
            print(f"Server: Error saving global model: {e}")

def load_global_model_from_disk():
    global global_model_weights
    if os.path.exists(config.GLOBAL_MODEL_SAVE_PATH):
        try:
            loaded_data = torch.load(config.GLOBAL_MODEL_SAVE_PATH)
            # Basic check if loaded data is a state_dict
            if isinstance(loaded_data, OrderedDict) and \
               all(isinstance(v, torch.Tensor) for v in loaded_data.values()):
                global_model_weights = loaded_data
                print(f"Server: Global model (state_dict) loaded from {config.GLOBAL_MODEL_SAVE_PATH}")
                # Optionally, determine INPUT_DIM from loaded model if possible (e.g. fc1.weight.shape[1])
                # This helps if server restarts and clients connect later.
                if 'fc1.weight' in global_model_weights and config.INPUT_DIM == -1:
                    try:
                        in_features = global_model_weights['fc1.weight'].shape[1]
                        if in_features > 0:
                            config.INPUT_DIM = in_features
                            print(f"Server: INPUT_DIM set to {config.INPUT_DIM} from loaded model.")
                    except Exception as e_dim:
                        print(f"Server: Could not determine INPUT_DIM from loaded model. Error: {e_dim}")
            else:
                print(f"Server: Loaded model from {config.GLOBAL_MODEL_SAVE_PATH} is not a valid state_dict. Starting fresh.")
                global_model_weights = None

        except Exception as e:
            print(f"Server: Error loading global model: {e}. Starting with no pre-loaded model.")
            global_model_weights = None
    else:
        print(f"Server: No pre-saved global model found at {config.GLOBAL_MODEL_SAVE_PATH}. Starting fresh.")


@app.route('/get_global_model', methods=['GET'])
def get_global_model_route():
    if global_model_weights:
        try:
            serializable_weights = weights_to_json_serializable(global_model_weights)
            return jsonify({'model_weights': serializable_weights, 'input_dim': config.INPUT_DIM})
        except Exception as e_ser:
            print(f"Server: Error serializing global model weights: {e_ser}")
            return jsonify({'model_weights': None, 'message': 'Error serializing model.', 'input_dim': config.INPUT_DIM}), 500
    else:
        return jsonify({'model_weights': None, 'message': 'Global model not initialized yet.', 'input_dim': config.INPUT_DIM})


@app.route('/submit_update', methods=['POST'])
def submit_update():
    # with aggregation_lock: # If using a lock
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received'}), 400
        
    client_id = data.get('client_id')
    weights_serializable = data.get('model_weights')
    data_size = data.get('data_size')

    if not all([client_id, weights_serializable, data_size is not None]):
        return jsonify({'status': 'error', 'message': 'Missing client_id, model_weights, or data_size'}), 400
    
    if client_id in connected_clients_this_round:
        return jsonify({'status': 'warning', 'message': f'Client {client_id} already submitted for this round.'}), 200 # Or 400

    try:
        client_model_weights = weights_from_json_serializable(weights_serializable)
        
        # Basic validation of received weights structure (e.g., check a known key)
        if global_model_weights and not all(key in client_model_weights for key in global_model_weights.keys()):
            print(f"Warning: Client {client_id} submitted weights with mismatched keys compared to global model.")
            # Decide how to handle: reject, or try to aggregate common keys (more complex)
            # For now, we'll proceed but this can cause issues in aggregate_updates if not careful.

        client_updates.append({'weights': client_model_weights, 'size': data_size, 'client_id': client_id})
        connected_clients_this_round.add(client_id)
        
        print(f"Server: Received update from {client_id} (data_size: {data_size}). "
              f"Total updates this round: {len(client_updates)}/{config.NUM_USERS}")

        # Aggregate if enough clients for this round have sent their updates
        # NUM_USERS in config should reflect the number of *active* clients expected per round.
        if len(client_updates) >= config.NUM_USERS:
            print(f"Server: Reached {len(client_updates)} updates, proceeding to aggregation.")
            aggregate_updates()
            save_global_model_to_disk() 
            client_updates.clear()
            connected_clients_this_round.clear()
            print("Server: Aggregation complete. Cleared updates for next round.")
            
        return jsonify({'status': 'success', 'message': 'Update received'})
    except Exception as e:
        print(f"Server: Error processing update from {client_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': f'Error processing update: {str(e)}'}), 500

def aggregate_updates():
    global global_model_weights
    if not client_updates:
        print("Server: No client updates to aggregate.")
        return

    total_data_size = sum(update['size'] for update in client_updates if update['size'] > 0) # Only consider clients with data
    
    if total_data_size == 0:
        print("Server: Total data size from updates is zero. Cannot perform weighted aggregation. Skipping.")
        # Optionally, could do unweighted average if sizes are problematic, or average of previous global model
        return

    # Initialize or use existing global_model_weights structure
    if global_model_weights is None:
        # Initialize from the first valid client update if no global model exists
        # Find first client with non-empty weights
        first_valid_update = next((upd for upd in client_updates if upd['weights']), None)
        if not first_valid_update:
            print("Server: No valid client weights to initialize global model structure. Skipping aggregation.")
            return
        template_weights = first_valid_update['weights']
        aggregated_weights = OrderedDict((key, torch.zeros_like(tensor)) for key, tensor in template_weights.items())
        print("Server: Initializing global model structure from first client update.")
    else:
        # Ensure new aggregated_weights are on CPU and float32 for consistency
        aggregated_weights = OrderedDict((key, torch.zeros_like(tensor, dtype=torch.float32, device='cpu')) 
                                         for key, tensor in global_model_weights.items())

    # Perform Federated Averaging (FedAvg)
    num_aggregated = 0
    for update_info in client_updates:
        client_w = update_info['weights']
        client_data_size = update_info['size']

        if client_data_size <= 0: # Skip clients that reported no data
            print(f"Server: Skipping update from {update_info['client_id']} due to data_size <= 0.")
            continue

        weighting_factor = client_data_size / total_data_size
        
        # Check for key mismatches before adding
        for key in aggregated_weights.keys():
            if key in client_w:
                if aggregated_weights[key].shape == client_w[key].shape:
                    aggregated_weights[key] += client_w[key].to(aggregated_weights[key].device, dtype=aggregated_weights[key].dtype) * weighting_factor
                else:
                    print(f"Server: Shape mismatch for key '{key}' from client {update_info['client_id']}. "
                          f"Global: {aggregated_weights[key].shape}, Client: {client_w[key].shape}. Skipping this key for this client.")
            else:
                print(f"Server: Key '{key}' not found in update from client {update_info['client_id']}. Skipping this key for this client.")
        num_aggregated +=1
        
    if num_aggregated > 0:
        global_model_weights = aggregated_weights
        print(f"Server: Global model updated via Federated Averaging from {num_aggregated} clients.")
    else:
        print("Server: No client updates were suitable for aggregation.")


if __name__ == '__main__':
    load_global_model_from_disk() 
    print(f"--- Federated Learning Server ---")
    print(f"Host: {config.SERVER_HOST}, Port: {config.SERVER_PORT}")
    print(f"Global Model Save Path: {config.GLOBAL_MODEL_SAVE_PATH}")
    print(f"Expected updates per round: {config.NUM_USERS}")
    print(f"Initial INPUT_DIM (from config or loaded model): {config.INPUT_DIM}")
    print(f"---------------------------------")
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=False) # debug=False for production/stable simulation