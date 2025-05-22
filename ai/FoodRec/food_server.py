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
    global global_model_weights, global_model_input_dim
    if os.path.exists(config.GLOBAL_MODEL_SAVE_PATH):
        try:
            loaded_data = torch.load(config.GLOBAL_MODEL_SAVE_PATH, map_location=torch.device('cpu')) # Load to CPU
            
            if isinstance(loaded_data, OrderedDict):
                # Ensure all loaded tensors that should be float are float.
                # This is a bit more defensive.
                corrected_state_dict = OrderedDict()
                temp_model_for_type_check = None
                if config.INPUT_DIM > 0 : # If we know INPUT_DIM, can instantiate a model for type checking
                    try:
                        temp_model_for_type_check = FoodPreferenceModel(input_dim=config.INPUT_DIM)
                    except ValueError: # If INPUT_DIM is not yet suitable for model
                        pass

                for k, v in loaded_data.items():
                    if isinstance(v, torch.Tensor):
                        # If we have a model instance, check parameter types
                        param_or_buffer = None
                        if temp_model_for_type_check:
                            try:
                                # This logic to get specific param/buffer is a bit complex
                                # and might fail if keys don't exactly match module hierarchy.
                                # A simpler approach is to assume learnable params are float.
                                # For example, 'weight' and 'bias' in names usually are.
                                if any(name_part in k for name_part in ['weight', 'bias']) and not v.is_floating_point():
                                    print(f"Warning: Loaded tensor '{k}' should be float but is {v.dtype}. Converting.")
                                    corrected_state_dict[k] = v.to(dtype=torch.float32)
                                else:
                                    corrected_state_dict[k] = v
                            except AttributeError: # if k not in model
                                corrected_state_dict[k] = v

                        elif ('.weight' in k or '.bias' in k) and not v.is_floating_point():
                            # Heuristic: 'weight' and 'bias' should be float.
                            print(f"Server (Load): Converting tensor '{k}' of type {v.dtype} to float32.")
                            corrected_state_dict[k] = v.to(dtype=torch.float32)
                        else:
                            corrected_state_dict[k] = v
                    else: # Should not happen if saved from state_dict
                        print(f"Server (Load): Item '{k}' in loaded data is not a tensor. Skipping.")
                        continue
                global_model_weights = corrected_state_dict
                print(f"Server: Global model (state_dict) loaded from {config.GLOBAL_MODEL_SAVE_PATH}")

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
            print(f"Server: Error loading global model: {e}. Starting fresh.")
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

    # Filter out clients with zero data size before calculating total_data_size
    valid_updates = [upd for upd in client_updates if upd.get('size', 0) > 0 and upd.get('weights')]
    if not valid_updates:
        print("Server: No valid client updates (with data_size > 0 and weights) to aggregate.")
        client_updates.clear() # Clear original list too
        connected_clients_this_round.clear()
        return

    total_data_size = sum(update['size'] for update in valid_updates)
    if total_data_size == 0: # Should be caught by valid_updates check, but as a safeguard
        print("Server: Total data size from valid updates is zero. Cannot perform weighted aggregation.")
        return

    # Initialize or use existing global_model_weights structure
    # Crucially, ensure tensors in aggregated_weights are FloatTensors for learnable params
    if global_model_weights is None:
        template_weights = valid_updates[0]['weights'] # Use the first valid update as template
        aggregated_weights = OrderedDict()
        for key, tensor in template_weights.items():
            # Only initialize for aggregation if it's a float tensor (learnable parameter)
            if tensor.is_floating_point():
                aggregated_weights[key] = torch.zeros_like(tensor, dtype=torch.float32, device='cpu')
            else:
                # For non-float tensors (like num_batches_tracked), copy from template (or handle differently)
                # Typically, these are not averaged. For simplicity, we might copy the first one
                # or decide not to include them in the global model that's averaged.
                # For FedAvg, we focus on learnable parameters.
                # If they must be part of the global_model_weights, decide strategy (e.g. take from one client)
                print(f"Server: Key '{key}' is not a float tensor (type: {tensor.dtype}). It will not be averaged by FedAvg. "
                      "It might be copied from the first client if global model is new.")
                aggregated_weights[key] = tensor.clone().detach().to('cpu') # Example: copy, not average

        print("Server: Initializing global model structure for aggregation.")
    else:
        aggregated_weights = OrderedDict()
        for key, tensor in global_model_weights.items():
            if tensor.is_floating_point():
                aggregated_weights[key] = torch.zeros_like(tensor, dtype=torch.float32, device='cpu')
            else:
                # If it's already in global_model_weights and not float, preserve it
                aggregated_weights[key] = tensor.clone().detach().to('cpu')


    num_aggregated_clients = 0
    for update_info in valid_updates: # Iterate over valid_updates
        client_w = update_info['weights']
        weighting_factor = update_info['size'] / total_data_size
        num_aggregated_clients += 1

        for key, agg_tensor in aggregated_weights.items():
            if key in client_w and client_w[key].is_floating_point() and agg_tensor.is_floating_point():
                # Ensure shapes match before attempting addition
                if agg_tensor.shape == client_w[key].shape:
                    # Ensure client tensor is also float and on CPU for the operation
                    # The error implies client_w[key] * weighting_factor is float, which is good.
                    # The issue is agg_tensor being Long.
                    # The fix is ensuring agg_tensor is initialized as Float (done above).
                    agg_tensor += client_w[key].to(device='cpu', dtype=torch.float32) * weighting_factor
                else:
                    print(f"Server: Shape mismatch for float key '{key}' from client {update_info['client_id']}. "
                          f"Global: {agg_tensor.shape}, Client: {client_w[key].shape}. Skipping this key for this client.")
            elif key in client_w and not client_w[key].is_floating_point():
                # If a non-float key exists (e.g. num_batches_tracked), and we decided to keep it in aggregated_weights
                # (e.g. by copying from the first client if global_model_weights was None),
                # we usually don't average it. The current aggregated_weights[key] would hold the copied value.
                # If we needed to update it (e.g. sum them, or take max), logic would go here.
                # For simple FedAvg of learnable params, we only operate on float tensors.
                pass # Do nothing for non-float tensors in this averaging loop.
            elif key not in client_w and agg_tensor.is_floating_point():
                 print(f"Server: Key '{key}' (float) not found in update from client {update_info['client_id']}. "
                       "Its contribution will be zero for this client.")


    if num_aggregated_clients > 0:
        global_model_weights = aggregated_weights # Update the global model
        print(f"Server: Global model updated via Federated Averaging from {num_aggregated_clients} clients.")
    else:
        print("Server: No client updates were suitable for aggregation in this round.")


if __name__ == '__main__':
    load_global_model_from_disk() 
    print(f"--- Federated Learning Server ---")
    print(f"Host: {config.SERVER_HOST}, Port: {config.SERVER_PORT}")
    print(f"Global Model Save Path: {config.GLOBAL_MODEL_SAVE_PATH}")
    print(f"Expected updates per round: {config.NUM_USERS}")
    print(f"Initial INPUT_DIM (from config or loaded model): {config.INPUT_DIM}")
    print(f"---------------------------------")
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=False) # debug=False for production/stable simulation