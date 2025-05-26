# food_server.py
from flask import Flask, request, jsonify
import torch
from collections import OrderedDict
import os
import federated_config as config
from food_model import FoodPreferenceModel, weights_from_json_serializable, weights_to_json_serializable

app = Flask(__name__)
global_model_weights = None
client_updates = []
connected_clients_this_round = set()
current_round_server = 0

def save_global_model_to_disk():
    if global_model_weights:
        try:
            torch.save(global_model_weights, config.GLOBAL_MODEL_SAVE_PATH)
            print(f"Server: Global model saved to {config.GLOBAL_MODEL_SAVE_PATH}")
        except Exception as e: print(f"Server: Error saving global model: {e}")

def load_global_model_from_disk():
    global global_model_weights
    if os.path.exists(config.GLOBAL_MODEL_SAVE_PATH):
        try:
            loaded_data = torch.load(config.GLOBAL_MODEL_SAVE_PATH, map_location=torch.device('cpu'))
            if isinstance(loaded_data, OrderedDict) and all(isinstance(v, torch.Tensor) for v in loaded_data.values()):
                global_model_weights = loaded_data
                print(f"Server: Global model loaded from {config.GLOBAL_MODEL_SAVE_PATH}")
                if 'fc1.weight' in global_model_weights and config.INPUT_DIM == -1:
                    dim = global_model_weights['fc1.weight'].shape[1]
                    if dim > 0: config.INPUT_DIM = dim; print(f"Server: INPUT_DIM set to {dim} from model.")
            else: print(f"Server: Loaded model from {config.GLOBAL_MODEL_SAVE_PATH} not valid state_dict.")
        except Exception as e: print(f"Server: Error loading model: {e}.")
    else: print(f"Server: No pre-saved model at {config.GLOBAL_MODEL_SAVE_PATH}.")


@app.route('/get_global_model', methods=['GET'])
def get_global_model_route():
    if global_model_weights:
        try:
            return jsonify({'model_weights': weights_to_json_serializable(global_model_weights), 'input_dim': config.INPUT_DIM})
        except Exception as e: return jsonify({'model_weights': None, 'message': f'Error serializing: {e}', 'input_dim': config.INPUT_DIM}), 500
    return jsonify({'model_weights': None, 'message': 'Global model not initialized yet.', 'input_dim': config.INPUT_DIM})

@app.route('/submit_update', methods=['POST'])
def submit_update():
    global current_round_server
    data = request.get_json()
    if not data: return jsonify({'status': 'error', 'message': 'No data received'}), 400
    client_id, weights_s, size, c_in_dim = data.get('client_id'), data.get('model_weights'), data.get('data_size'), data.get('input_dim', -1)

    if not all([client_id, weights_s, size is not None]):
        return jsonify({'status': 'error', 'message': 'Missing fields'}), 400
    if client_id in connected_clients_this_round:
        return jsonify({'status': 'warning', 'message': f'{client_id} already submitted.'}), 200

    try:
        client_weights = weights_from_json_serializable(weights_s)
        if config.INPUT_DIM == -1 and c_in_dim > 0:
            config.INPUT_DIM = c_in_dim
            print(f"Server: INPUT_DIM set to {config.INPUT_DIM} by first update from {client_id}.")
        elif c_in_dim > 0 and config.INPUT_DIM != c_in_dim:
            print(f"Warning: {client_id} (dim={c_in_dim}) mismatches server INPUT_DIM ({config.INPUT_DIM}).")
            # Potentially reject or handle carefully in aggregation

        client_updates.append({'weights': client_weights, 'size': size, 'client_id': client_id})
        connected_clients_this_round.add(client_id)
        print(f"Server: Rcvd update from {client_id} (size:{size}, dim:{c_in_dim if c_in_dim>0 else 'N/A'}). "
              f"Round updates: {len(client_updates)}/{config.NUM_USERS if config.NUM_USERS !=-1 else '?'}")

        # NUM_USERS in config should be updated by run_simulation based on actual clients
        print(f"======================================{len(client_updates)} / {config.NUM_USERS} ================================")
        if config.NUM_USERS > 0 and len(client_updates) >= config.NUM_USERS:
            print(f"Server: Reached {len(client_updates)} updates, aggregating...")
            aggregate_updates()
            save_global_model_to_disk()
            client_updates.clear(); connected_clients_this_round.clear(); current_round_server += 1
            print(f"Server: Aggregation for round {current_round_server} complete.")
        return jsonify({'status': 'success', 'message': 'Update received'})
    except Exception as e:
        print(f"Server: Error processing update from {client_id}: {e}"); import traceback; traceback.print_exc()
        return jsonify({'status': 'error', 'message': f'Error: {e}'}), 500

def aggregate_updates():
    global global_model_weights
    if not client_updates: print("Server: No updates to aggregate."); return
    valid_updates = [upd for upd in client_updates if upd['size'] > 0 and upd['weights']]
    if not valid_updates: print("Server: No valid updates (with size > 0 and weights)."); return

    total_data_size = sum(upd['size'] for upd in valid_updates)
    if total_data_size == 0: print("Server: Total data size is zero. Skipping aggregation."); return

    if global_model_weights is None:
        if config.INPUT_DIM == -1:
            print("Server: CRITICAL - INPUT_DIM is -1 during aggregation. Cannot create model template.")
            return
        try:
            print(f"Server: Initializing global model for aggregation with INPUT_DIM: {config.INPUT_DIM}")
            model_template = FoodPreferenceModel(input_dim=config.INPUT_DIM)
            # --- MODIFICATION: Initialize with float32 and only for relevant keys ---
            global_model_weights = OrderedDict()
            for k, v in model_template.state_dict().items():
                if v.is_floating_point(): # Only consider float parameters for aggregation
                    global_model_weights[k] = torch.zeros_like(v, dtype=torch.float32, device='cpu')
                # else: # Optionally handle non-float parameters (e.g., num_batches_tracked)
                      # For num_batches_tracked, often it's reset or taken from one client, not averaged.
                      # For simplicity here, we are only averaging float parameters.
                      # If you need to handle num_batches_tracked, it's usually reset or taken from one client.
                      # global_model_weights[k] = v.clone().to(device='cpu') # Example: just copy it
            if not global_model_weights:
                print("Server: ERROR - No floating point parameters found in model template to initialize global_model_weights.")
                return
            print(f"Server: Global model weights structure initialized with {len(global_model_weights)} floating point parameter groups.")
        except Exception as e_agg_init:
            print(f"Server: ERROR creating model template for aggregation (INPUT_DIM: {config.INPUT_DIM}): {e_agg_init}"); return

    # Zero out current global_model_weights' floating point parameters before summing new updates
    for key in global_model_weights.keys():
        if global_model_weights[key].is_floating_point(): # Ensure we only zero out what we will aggregate
            global_model_weights[key].zero_()

    num_aggregated_clients = 0
    for upd in valid_updates:
        client_w, client_size, client_id_str = upd['weights'], upd['size'], upd['client_id']
        factor = client_size / total_data_size
        
        compatible_update_for_aggregation = True
        for key in global_model_weights.keys(): # Iterate over keys in our float-only global_model_weights
            if key not in client_w:
                print(f"Server: Key '{key}' missing in update from {client_id_str}. Skipping this client for this key.")
                # This might be acceptable if we are only aggregating common float keys
                # However, for FedAvg, usually all clients should send all model params.
                # For now, this check means if a float key is missing, the client update might be problematic.
                compatible_update_for_aggregation = False; break
            if not client_w[key].is_floating_point():
                # print(f"Server: Client {client_id_str} sent non-float tensor for key '{key}'. Skipping this key for this client.")
                continue # Skip non-float keys from client for aggregation
            if global_model_weights[key].shape != client_w[key].shape:
                print(f"Server: Shape mismatch for key '{key}' from {client_id_str}. Global: {global_model_weights[key].shape}, Client: {client_w[key].shape}. Skipping this client's update.")
                compatible_update_for_aggregation = False; break
        
        if not compatible_update_for_aggregation:
            continue # Skip this entire client update if a critical incompatibility is found

        aggregated_at_least_one_key_for_this_client = False
        for key in global_model_weights.keys(): # These are the float keys we care about
            if key in client_w and client_w[key].is_floating_point(): # Double check client's key is float
                # --- MODIFICATION: Ensure client tensor is also float before adding ---
                try:
                    global_model_weights[key] += client_w[key].to(global_model_weights[key].device, dtype=torch.float32) * factor
                    aggregated_at_least_one_key_for_this_client = True
                except RuntimeError as e: # Catch type errors here specifically
                    print(f"Server: RuntimeError during aggregation for key '{key}' from {client_id_str}. Error: {e}. Skipping this key.")
                    print(f"  Global tensor '{key}' dtype: {global_model_weights[key].dtype}")
                    print(f"  Client tensor '{key}' dtype: {client_w[key].dtype}")

        if aggregated_at_least_one_key_for_this_client:
            num_aggregated_clients += 1

    if num_aggregated_clients > 0:
        print(f"Server: Global model updated from {num_aggregated_clients} clients.")
    else:
        # If no clients were aggregated, global_model_weights might still be all zeros from initialization
        # or from the previous round if it was not None before.
        # It's important that if it was None, it should remain None or be set to a valid model state.
        # The current logic re-initializes it to zeros if it was None.
        # If it was not None, it just zeros it out.
        print("Server: No client updates were compatible for aggregation this round.")
        

if __name__ == '__main__':
    load_global_model_from_disk()
    print(f"--- Shanghai Food FL Server ---")
    print(f"Host: {config.SERVER_HOST}, Port: {config.SERVER_PORT}")
    # config.NUM_USERS is set by simulation script when it starts
    print(f"Initial INPUT_DIM: {config.INPUT_DIM}")
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=False, use_reloader=False)