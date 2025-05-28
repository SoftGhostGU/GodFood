# food_server.py (Combined FL Server, Recommendation API, and Training API)
from flask import Flask, request, jsonify
import torch
from torch.utils.data import Dataset, DataLoader # DataLoader needed by Client
import torch.optim as optim # Needed by Client
import torch.nn as nn # Needed by Client
import pandas as pd
import numpy as np
from collections import OrderedDict
import os
import json
import joblib
import io
import time
import threading # For Client's preprocessor lock
import random
import traceback # For printing tracebacks

# --- Configuration & Model Imports ---
import federated_config as config
from food_model import FoodPreferenceModel, weights_to_json_serializable, weights_from_json_serializable
from food_data_generator import load_csv_to_dataframe, get_shanghai_data_for_simulation

# --- Import Client and its dependencies ---
# The ReviewDataset and preprocessor functions are defined within food_client now,
# but we'll use the versions defined/adapted in this server file for consistency for the API parts.
# The Client class itself will be imported.
from food_client import Client, ReviewDataset, create_preprocessor as create_client_preprocessor, process_features_for_recommendation as client_process_reco_features

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# === Global Variables for the Combined Server ===
fl_global_model_weights = None
fl_client_updates = []
fl_connected_clients_this_round = set()
fl_current_round_server = 0

api_all_restaurants_df = None
api_preprocessor = None # Global preprocessor for API use
api_input_dim = -1      # Global input_dim for API use
reco_inference_model = None

# === Preprocessing Logic (Server's version for APIs) ===
# This create_api_preprocessor will be used to initialize api_preprocessor.
# Client instances will use their own static preprocessor logic, but we'll try to sync them.
def create_api_preprocessor_server():
    categorical_pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    numerical_pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', categorical_pipeline, config.CATEGORY_COLS),
            ('num', numerical_pipeline, config.NUMERIC_COLS)
        ],
        remainder='drop', n_jobs=-1
    )
    return preprocessor

def process_features_for_api_recommendation(preprocessor, user_context_dict, all_restaurants_df_orig):
    if all_restaurants_df_orig.empty: return torch.empty(0), [], 0
    all_restaurants_df = all_restaurants_df_orig.copy()
    inference_df_list = []
    restaurant_ids_order = []
    user_base_df = pd.DataFrame([user_context_dict])
    for _, restaurant_row_series in all_restaurants_df.iterrows():
        restaurant_row = restaurant_row_series.to_dict()
        combined_features_df = user_base_df.copy()
        for col, val in restaurant_row.items():
            if col in config.CATEGORY_COLS or col in config.NUMERIC_COLS:
                 combined_features_df[col] = val
        inference_df_list.append(combined_features_df)
        restaurant_ids_order.append(restaurant_row['restaurant_id'])
    if not inference_df_list: return torch.empty(0), [], 0
    full_inference_df = pd.concat(inference_df_list, ignore_index=True)
    all_expected_feature_cols = config.CATEGORY_COLS + config.NUMERIC_COLS
    for col in all_expected_feature_cols:
        if col not in full_inference_df.columns: full_inference_df[col] = np.nan
    try:
        X_to_process = full_inference_df[all_expected_feature_cols]
        X_processed = preprocessor.transform(X_to_process)
    except Exception as e:
        print(f"API Server: Error during preproc transform for recommendation: {e}")
        return torch.empty(0), [], 0
    return torch.tensor(X_processed, dtype=torch.float32), restaurant_ids_order, X_processed.shape[1]


# === Federated Learning Server Core Logic ===
def save_fl_global_model_to_disk():
    global fl_global_model_weights
    if fl_global_model_weights:
        try:
            torch.save(fl_global_model_weights, config.GLOBAL_MODEL_SAVE_PATH)
            print(f"FL Server: Global model saved to {config.GLOBAL_MODEL_SAVE_PATH}")
        except Exception as e: print(f"FL Server: Error saving global model: {e}")

def load_fl_global_model_from_disk():
    global fl_global_model_weights, api_input_dim
    if os.path.exists(config.GLOBAL_MODEL_SAVE_PATH):
        try:
            loaded_data = torch.load(config.GLOBAL_MODEL_SAVE_PATH, map_location=torch.device('cpu'))
            if isinstance(loaded_data, OrderedDict) and all(isinstance(v, torch.Tensor) for v in loaded_data.values()):
                fl_global_model_weights = loaded_data
                print(f"FL Server: Global model loaded from {config.GLOBAL_MODEL_SAVE_PATH}")
                if 'fc1.weight' in fl_global_model_weights:
                    dim = fl_global_model_weights['fc1.weight'].shape[1]
                    if dim > 0:
                        if config.INPUT_DIM == -1: config.INPUT_DIM = dim
                        if api_input_dim == -1: api_input_dim = dim # Sync with API's global dim
                        print(f"FL Server: INPUT_DIM set to {dim} from loaded model.")
            else: print(f"FL Server: Loaded model from {config.GLOBAL_MODEL_SAVE_PATH} not valid state_dict.")
        except Exception as e: print(f"FL Server: Error loading model: {e}.")
    else: print(f"FL Server: No pre-saved FL model at {config.GLOBAL_MODEL_SAVE_PATH}.")

@app.route('/get_global_model', methods=['GET']) # FL Endpoint
def get_fl_global_model_route():
    global fl_global_model_weights, api_input_dim
    current_dim_to_send = api_input_dim if api_input_dim > 0 else config.INPUT_DIM
    if fl_global_model_weights:
        try:
            model_dim_check = -1
            if 'fc1.weight' in fl_global_model_weights: model_dim_check = fl_global_model_weights['fc1.weight'].shape[1]
            if model_dim_check > 0 and current_dim_to_send > 0 and model_dim_check != current_dim_to_send:
                print(f"FL Server WARNING in /get_global_model: model actual dim {model_dim_check} != reported dim {current_dim_to_send}. Reporting actual.")
                current_dim_to_send = model_dim_check
            elif model_dim_check > 0 and current_dim_to_send <=0:
                 current_dim_to_send = model_dim_check

            return jsonify({'model_weights': weights_to_json_serializable(fl_global_model_weights),
                            'input_dim': current_dim_to_send})
        except Exception as e:
            print(f"FL Server ERROR in /get_global_model serialization: {e}"); traceback.print_exc()
            return jsonify({'model_weights': None, 'message': f'Error serializing: {e}',
                            'input_dim': current_dim_to_send}), 500
    return jsonify({'model_weights': None, 'message': 'FL Global model not initialized yet.',
                    'input_dim': current_dim_to_send})

@app.route('/submit_update', methods=['POST']) # FL Endpoint
def submit_fl_update_route():
    global fl_current_round_server, fl_client_updates, fl_connected_clients_this_round, api_input_dim, config

    data = request.get_json()
    if not data: return jsonify({'status': 'error', 'message': 'No data received'}), 400
    client_id, weights_s, size, c_in_dim = data.get('client_id'), data.get('model_weights'), data.get('data_size'), data.get('input_dim', -1)

    if not all([client_id, weights_s, size is not None]):
        return jsonify({'status': 'error', 'message': 'Missing fields'}), 400
    if client_id in fl_connected_clients_this_round:
        return jsonify({'status': 'warning', 'message': f'{client_id} already submitted for this FL round.'}), 200

    try:
        client_weights = weights_from_json_serializable(weights_s)
        if config.INPUT_DIM == -1 and c_in_dim > 0:
            config.INPUT_DIM = c_in_dim
            if api_input_dim == -1 : api_input_dim = c_in_dim
            print(f"FL Server: config.INPUT_DIM set to {config.INPUT_DIM} by first update from {client_id}.")
        elif c_in_dim > 0 and config.INPUT_DIM != c_in_dim:
            print(f"FL Server WARNING: Update from {client_id} (dim={c_in_dim}) "
                  f"mismatches server's expected INPUT_DIM ({config.INPUT_DIM}). Client should align.")

        fl_client_updates.append({'weights': client_weights, 'size': size, 'client_id': client_id})
        fl_connected_clients_this_round.add(client_id)
        print(f"FL Server: Rcvd update from {client_id} (size:{size}, dim:{c_in_dim if c_in_dim>0 else 'N/A'}). "
              f"Round updates: {len(fl_client_updates)}/{config.NUM_USERS if config.NUM_USERS !=-1 else '?'}")

        if config.NUM_USERS > 0 and len(fl_client_updates) >= config.NUM_USERS:
            print(f"FL Server: Reached {len(fl_client_updates)} updates for FL round, aggregating...")
            aggregate_fl_updates() # This will use and potentially set config.INPUT_DIM, api_input_dim
            save_fl_global_model_to_disk()
            fl_client_updates.clear(); fl_connected_clients_this_round.clear(); fl_current_round_server += 1
            print(f"FL Server: Aggregation for FL round {fl_current_round_server} complete.")
        return jsonify({'status': 'success', 'message': 'FL Update received'})
    except Exception as e:
        print(f"FL Server: Error processing FL update from {client_id}: {e}"); traceback.print_exc()
        return jsonify({'status': 'error', 'message': f'Error: {e}'}), 500

def aggregate_fl_updates():
    global fl_global_model_weights, fl_client_updates, api_input_dim, config
    if not fl_client_updates: print("FL Server: No updates to aggregate."); return
    valid_updates = [upd for upd in fl_client_updates if upd['size'] > 0 and upd['weights']]
    if not valid_updates: print("FL Server: No valid FL updates."); return
    total_data_size = sum(upd['size'] for upd in valid_updates)
    if total_data_size == 0: print("FL Server: Total data size for FL is zero."); return

    current_aggregation_input_dim = api_input_dim if api_input_dim > 0 else config.INPUT_DIM
    if current_aggregation_input_dim <= 0:
        for upd_check_dim in valid_updates:
            if 'fc1.weight' in upd_check_dim['weights']:
                current_aggregation_input_dim = upd_check_dim['weights']['fc1.weight'].shape[1]
                print(f"FL Server: Deduced aggregation INPUT_DIM as {current_aggregation_input_dim} from first client update.")
                if api_input_dim == -1: api_input_dim = current_aggregation_input_dim
                if config.INPUT_DIM == -1: config.INPUT_DIM = current_aggregation_input_dim
                break
        if current_aggregation_input_dim <= 0:
            print("FL Server: CRITICAL - INPUT_DIM unknown for aggregation. Cannot proceed.")
            return

    if fl_global_model_weights is None:
        try:
            print(f"FL Server: Initializing FL global model for aggregation with INPUT_DIM: {current_aggregation_input_dim}")
            model_template = FoodPreferenceModel(input_dim=current_aggregation_input_dim)
            fl_global_model_weights = OrderedDict()
            for k, v_template in model_template.state_dict().items():
                if v_template.is_floating_point(): fl_global_model_weights[k] = torch.zeros_like(v_template, dtype=torch.float32, device='cpu')
            if not fl_global_model_weights: print("FL Server: ERROR - No float params in model template."); return
        except Exception as e_agg_init: print(f"FL Server: ERROR creating model template (dim {current_aggregation_input_dim}): {e_agg_init}"); return

    for key_g in fl_global_model_weights.keys():
        if fl_global_model_weights[key_g].is_floating_point(): fl_global_model_weights[key_g].zero_()
    num_aggregated_clients = 0
    for upd_agg in valid_updates:
        client_w, client_size, client_id_str = upd_agg['weights'], upd_agg['size'], upd_agg['client_id']
        factor = client_size / total_data_size; compatible = True
        for key_g_check in fl_global_model_weights.keys():
            if key_g_check not in client_w: compatible = False; print(f"FL Server: Key '{key_g_check}' missing from {client_id_str}."); break
            if not client_w[key_g_check].is_floating_point(): continue
            if fl_global_model_weights[key_g_check].shape != client_w[key_g_check].shape:
                compatible = False; print(f"FL Server: Shape mismatch for '{key_g_check}' from {client_id_str}. Global {fl_global_model_weights[key_g_check].shape}, Client {client_w[key_g_check].shape}."); break
        if not compatible: continue
        for key_g_agg in fl_global_model_weights.keys():
            if key_g_agg in client_w and client_w[key_g_agg].is_floating_point():
                try: fl_global_model_weights[key_g_agg] += client_w[key_g_agg].to(fl_global_model_weights[key_g_agg].device, dtype=torch.float32) * factor
                except RuntimeError as e_rt: print(f"FL Server: Aggregation RuntimeError for '{key_g_agg}' from {client_id_str}: {e_rt}")
        num_aggregated_clients +=1
    if num_aggregated_clients > 0: print(f"FL Server: FL Global model updated from {num_aggregated_clients} clients.")
    else: print("FL Server: No client updates were compatible for FL aggregation this round.")

# === Recommendation API Logic ===
@app.route('/recommend', methods=['POST'])
def recommend_route():
    global api_all_restaurants_df, reco_inference_model, api_preprocessor, api_input_dim
    if api_all_restaurants_df is None or reco_inference_model is None or api_preprocessor is None or api_input_dim <= 0:
        return jsonify({"error": "Recommendation server resources not ready."}), 503
    user_context = request.get_json()
    if not user_context: return jsonify({"error": "Invalid input: No JSON payload."}), 400
    all_user_side_features_expected = [col for col in config.CATEGORY_COLS + config.NUMERIC_COLS if col not in api_all_restaurants_df.columns]
    for col in all_user_side_features_expected:
        if col not in user_context: user_context[col] = "Unknown" if col in config.CATEGORY_COLS else 0.0
    try:
        features_tensor, restaurant_ids_order, num_feat_proc = process_features_for_api_recommendation(
            api_preprocessor, user_context, api_all_restaurants_df)
    except Exception as e: return jsonify({"error": f"Feature processing error: {str(e)}"}), 500
    if features_tensor.nelement() == 0: return jsonify({"message": "No features processed.", "recommendations": []})
    if num_feat_proc != api_input_dim: return jsonify({"error": f"Feature mismatch! Model expects {api_input_dim}, Preproc: {num_feat_proc}."}), 500
    reco_inference_model.eval()
    with torch.no_grad():
        logits = reco_inference_model(features_tensor); probs = torch.softmax(logits, dim=1)
        high_pref_scores = probs[:, 2]
        if high_pref_scores.numel() == 0: return jsonify({"message": "No scores generated.", "recommendations": []})
        k = min(20, high_pref_scores.numel(), len(restaurant_ids_order))
        if k == 0: return jsonify({"message": "Not enough data for recs.", "recommendations": []})
        top_scores_t, top_indices_t = torch.topk(high_pref_scores, k=k)
        rec_ids = [restaurant_ids_order[i] for i in top_indices_t.tolist()]
        top_recs_df = api_all_restaurants_df[api_all_restaurants_df['restaurant_id'].isin(rec_ids)].copy()
        id_score_map_inf = dict(zip(rec_ids, top_scores_t.tolist()))
        top_recs_df['recommendation_score'] = top_recs_df['restaurant_id'].map(id_score_map_inf)
        recs_output = top_recs_df.sort_values(by='recommendation_score', ascending=False).fillna('N/A').to_dict(orient='records')
    return jsonify({"recommendations": recs_output})

def csv_string_to_dataframe(csv_string):
    if not csv_string or not isinstance(csv_string, str): return pd.DataFrame()
    try: return pd.read_csv(io.StringIO(csv_string))
    except Exception as e: print(f"Error converting CSV string to DataFrame: {e}"); return pd.DataFrame()

# === User-Specific Training API Logic ===
@app.route('/train_user_model', methods=['POST'])
def train_user_model_route():
    global api_all_restaurants_df, api_preprocessor, api_input_dim, config # Uses shared resources
    if api_all_restaurants_df is None or Client._shared_preprocessor is None: # Check Client's preprocessor
        # Note: api_preprocessor is the server's global one. Client manages its own static var.
        # They should be the same instance after load_all_global_resources.
        return jsonify({"error": "Training API resources (restaurants or client preprocessor) not loaded."}), 503

    content_type = request.headers.get('Content-Type')
    user_reviews_csv_string = None
    if 'application/json' in content_type:
        data = request.get_json(); user_reviews_csv_string = data.get('user_reviews_csv')
        if not user_reviews_csv_string: return jsonify({"error": "Missing 'user_reviews_csv'."}), 400
    elif 'text/csv' in content_type or 'text/plain' in content_type:
        user_reviews_csv_string = request.data.decode('utf-8')
    else: return jsonify({"error": "Unsupported Content-Type."}), 415

    client_review_data = csv_string_to_dataframe(user_reviews_csv_string)
    if client_review_data.empty: return jsonify({"error": "User review data empty/invalid."}), 400
    if 'user_id' not in client_review_data.columns or client_review_data['user_id'].nunique() != 1:
        return jsonify({"error": "'user_id' missing or not unique."}), 400
    client_id_str = str(client_review_data['user_id'].iloc[0])
    
    profile_cols = [col for col in config.USER_PROFILE_COLS if col in client_review_data.columns]
    user_profile_series = client_review_data.iloc[0][profile_cols] if profile_cols else None
    
    server_url_for_client = f"http://{config.SERVER_HOST}:{config.SERVER_PORT}"

    try:
        # Use the imported food_client.Client
        # It will use its own static preprocessor logic, which should have been
        # initialized by load_all_global_resources via Client._shared_preprocessor
        client_instance = Client(
            client_id=client_id_str,
            reviews_df_for_client=client_review_data.copy(),
            all_restaurants_df=api_all_restaurants_df, # Server's global restaurant data
            server_url=server_url_for_client,
            user_enhanced_profile_series=user_profile_series
        )
    except Exception as e_init:
        print(f"Training API ERROR: Client {client_id_str} init failed: {e_init}"); traceback.print_exc()
        return jsonify({"error": f"Client init failed: {str(e_init)}"}), 500
    
    if not client_instance.model or client_instance.input_dim <= 0:
        # Check api_input_dim as Client might update config.INPUT_DIM which api_input_dim tracks
        if api_input_dim > 0 and (not client_instance.model or client_instance.input_dim <=0 ):
            print(f"Training API Info: Client {client_id_str} model error, but global api_input_dim ({api_input_dim}) is set. Trying to re-init client model.")
            try:
                client_instance.input_dim = api_input_dim
                client_instance.model = FoodPreferenceModel(input_dim=api_input_dim)
                print(f"Training API Info: Re-initialized client {client_id_str} model with input_dim {api_input_dim}")
            except Exception as e_reinit:
                print(f"Training API Error: Failed to re-init client {client_id_str} model: {e_reinit}")
                return jsonify({"error": f"Client model not init or invalid input_dim ({client_instance.input_dim}). Re-init failed."}), 500
        else:
            return jsonify({"error": f"Client model not init or invalid input_dim ({client_instance.input_dim})."}), 500

    # Client makes an HTTP call to /get_global_model (on this same server)
    client_instance.get_global_model() 
    # Check if model is still valid after get_global_model, as it might reinitialize
    if not client_instance.model:
        msg = f"Client {client_id_str}: Model became invalid after get_global_model. Cannot train."
        print(f"Training API WARNING: {msg}")
        return jsonify({"warning": msg, "message": "Training not performed."}), 202

    avg_loss = client_instance.train_local_model() # Uses Client's internal LOCAL_EPOCHS or API_TRAIN_EPOCHS if Client is adapted
    
    update_sent_status_message = "NotAttempted"
    if config.API_SEND_UPDATE_TO_SERVER:
        print(f"Training API: Client {client_id_str} attempting to send update via HTTP POST.")
        # Client makes an HTTP call to /submit_update (on this same server)
        # We need to capture the outcome of this. Client.send_local_update() doesn't return status well.
        # For simplicity, we assume it prints errors. A more robust way would be for send_local_update to return success/failure.
        client_instance.send_local_update() 
        # This is tricky to get direct feedback from an HTTP call within an HTTP call's handler
        # We're relying on the server's aggregation logic to pick it up if NUM_USERS=1 or similar
        update_sent_status_message = "AttemptedHttpSend" 
        # If the FL server part (submit_fl_update_route) aggregates immediately due to NUM_USERS,
        # then fl_global_model_weights would be updated.

    return jsonify({
        "user_id": client_id_str, "status": "Training process completed.",
        "training_samples": len(client_instance.train_dataset) if client_instance.train_dataset else 0,
        "avg_loss_last_epoch": avg_loss if avg_loss is not None else "N/A",
        "input_dim_used": client_instance.input_dim,
        "update_sent_to_fl_server": update_sent_status_message
    }), 200

# === Combined Server Initialization ===
def _infer_input_dim_from_state_dict(state_dict):
    if state_dict and 'fc1.weight' in state_dict: return state_dict['fc1.weight'].shape[1]
    return -1

def load_all_global_resources():
    global api_all_restaurants_df, api_preprocessor, api_input_dim, reco_inference_model, fl_global_model_weights, config

    print("--- Combined Server: Loading ALL Global Resources ---")
    load_fl_global_model_from_disk() # Populates fl_global_model_weights, can set config.INPUT_DIM, api_input_dim

    _, restaurants_df_from_generator = get_shanghai_data_for_simulation()
    if restaurants_df_from_generator.empty: print("CRITICAL: No Shanghai restaurant data for API. Exiting."); exit(1)
    api_all_restaurants_df = restaurants_df_from_generator
    if 'id' in api_all_restaurants_df.columns: api_all_restaurants_df.rename(columns={'id': 'restaurant_id'}, inplace=True)
    if 'rating' in api_all_restaurants_df.columns: api_all_restaurants_df.rename(columns={'rating': 'rating_biz'}, inplace=True)
    print(f"API Server: Loaded {len(api_all_restaurants_df)} Shanghai restaurants.")

    if os.path.exists(config.PREPROCESSOR_SAVE_PATH):
        try:
            loaded_preprocessor = joblib.load(config.PREPROCESSOR_SAVE_PATH)
            api_preprocessor = loaded_preprocessor # For API direct use
            Client._shared_preprocessor = loaded_preprocessor # For Client instances
            Client._preprocessor_fitted_and_saved = True      # Update Client static vars
            print(f"API Server: Loaded shared preprocessor from {config.PREPROCESSOR_SAVE_PATH} for API and Client class.")
            if api_input_dim == -1 and hasattr(api_preprocessor, 'transformers_'):
                dummy_df_cols = config.CATEGORY_COLS + config.NUMERIC_COLS
                temp_data = {col: [np.nan] for col in dummy_df_cols}
                dummy_df_for_shape = pd.DataFrame(temp_data, columns=dummy_df_cols)
                try:
                    transformed_dummy = api_preprocessor.transform(dummy_df_for_shape[config.CATEGORY_COLS + config.NUMERIC_COLS])
                    inferred_dim = transformed_dummy.shape[1]
                    if inferred_dim > 0:
                        api_input_dim = inferred_dim
                        if config.INPUT_DIM == -1: config.INPUT_DIM = inferred_dim
                        print(f"API Server: Inferred INPUT_DIM={api_input_dim} from loaded preprocessor.")
                except Exception as e_trans_dummy: print(f"API Server: Could not infer INPUT_DIM from preprocessor: {e_trans_dummy}")
        except Exception as e_load_p:
            print(f"API Server: Preprocessor load FAILED: {e_load_p}. CRITICAL: Preprocessor must be pre-trained."); exit(1)
    else:
        print(f"API Server: CRITICAL - Preprocessor not found at {config.PREPROCESSOR_SAVE_PATH}. Must be pre-trained."); exit(1)

    if not os.path.exists(config.GLOBAL_MODEL_SAVE_PATH):
        print(f"API Server WARNING: Recommendation model {config.GLOBAL_MODEL_SAVE_PATH} not found. /recommend might fail until FL model is trained.")
        reco_inference_model = None # No static model for reco
    else:
        try:
            reco_model_state_dict = torch.load(config.GLOBAL_MODEL_SAVE_PATH, map_location=torch.device('cpu'))
            dim_from_reco_model = _infer_input_dim_from_state_dict(reco_model_state_dict)
            if api_input_dim == -1 and dim_from_reco_model > 0:
                api_input_dim = dim_from_reco_model
                if config.INPUT_DIM == -1: config.INPUT_DIM = api_input_dim
                print(f"API Server: INPUT_DIM set to {api_input_dim} from recommendation model.")
            elif api_input_dim > 0 and dim_from_reco_model > 0 and api_input_dim != dim_from_reco_model:
                print(f"API Server WARNING: api_input_dim ({api_input_dim}) differs from reco model's dim ({dim_from_reco_model}). Using {api_input_dim}.")
            if api_input_dim <= 0: print(f"API Server CRITICAL: Final INPUT_DIM for reco model is {api_input_dim}. Exiting."); exit(1)
            reco_inference_model = FoodPreferenceModel(input_dim=api_input_dim)
            reco_inference_model.load_state_dict(reco_model_state_dict, strict=False)
            reco_inference_model.eval()
            print(f"API Server: Recommendation model weights loaded (INPUT_DIM: {api_input_dim}).")
        except Exception as e: print(f"API Server WARNING: Error loading recommendation model: {e}. /recommend may fail."); reco_inference_model = None

    # Ensure config.INPUT_DIM and api_input_dim are synchronized. api_input_dim is leading.
    if api_input_dim > 0:
        if config.INPUT_DIM != api_input_dim :
             print(f"API Server: Synchronizing config.INPUT_DIM ({config.INPUT_DIM}) to api_input_dim ({api_input_dim}).")
             config.INPUT_DIM = api_input_dim
    elif config.INPUT_DIM > 0: # api_input_dim was not set, use config.INPUT_DIM
        api_input_dim = config.INPUT_DIM
        print(f"API Server: Setting api_input_dim from config.INPUT_DIM to {api_input_dim}.")
    else: # Still no valid dimension
        print("API Server CRITICAL: Could not determine a valid INPUT_DIM. Exiting.")
        exit(1)
        
    print(f"--- Combined Server: All global resources loaded. Final effective INPUT_DIM: {api_input_dim} ---")

if __name__ == '__main__':
    if not hasattr(config, 'USER_PROFILE_COLS'): print("CRITICAL: 'USER_PROFILE_COLS' not defined in config."); exit(1)
    if not hasattr(config, 'API_TRAIN_EPOCHS'): config.API_TRAIN_EPOCHS = 1
    if not hasattr(config, 'API_SEND_UPDATE_TO_SERVER'): config.API_SEND_UPDATE_TO_SERVER = True
    
    load_all_global_resources()
    print(f"--- Combined Food Server (FL, Recommendation, Training) ---")
    print(f"Host: {config.SERVER_HOST}, Port: {config.SERVER_PORT}")
    print(f"Federated Learning NUM_USERS configured to: {config.NUM_USERS} (can be dynamic for API calls)")
    print(f"Effective INPUT_DIM for operations: {api_input_dim}")
    # Run with threaded=True to allow Client's HTTP calls to this same server process
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=True, use_reloader=False, threaded=True)