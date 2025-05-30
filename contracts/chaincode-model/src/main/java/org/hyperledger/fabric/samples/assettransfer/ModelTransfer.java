/*
 * SPDX-License-Identifier: Apache-2.0
 */

package org.hyperledger.fabric.samples.assettransfer;

import java.io.IOException;
import java.util.*;
import java.util.stream.Collectors;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.hyperledger.fabric.contract.Context;
import org.hyperledger.fabric.contract.ContractInterface;
import org.hyperledger.fabric.contract.annotation.Contact;
import org.hyperledger.fabric.contract.annotation.Contract;
import org.hyperledger.fabric.contract.annotation.Default;
import org.hyperledger.fabric.contract.annotation.Info;
import org.hyperledger.fabric.contract.annotation.License;
import org.hyperledger.fabric.contract.annotation.Transaction;
import org.hyperledger.fabric.shim.ChaincodeException;
import org.hyperledger.fabric.shim.ChaincodeStub;
import org.hyperledger.fabric.shim.ledger.KeyValue;
import org.hyperledger.fabric.shim.ledger.QueryResultsIterator;
import com.owlike.genson.Genson;
import org.json.JSONObject;
import org.json.JSONPointer;

@Contract(name = "model", info = @Info(title = "Model Transfer", description = "The hyperlegendary model transfer", version = "0.0.1-SNAPSHOT", license = @License(name = "Apache 2.0 License", url = "http://www.apache.org/licenses/LICENSE-2.0.html"), contact = @Contact(email = "a.transfer@example.com", name = "Adrian Transfer", url = "https://hyperledger.example.com")))
@Default
public final class ModelTransfer implements ContractInterface {

    private final Genson genson = new Genson();

    private enum AssetTransferErrors {
        ASSET_NOT_FOUND,
        ASSET_ALREADY_EXISTS
    }

    private static Map<String, Map<String, List<List<Double>>>> channelModels = new HashMap<>();

    /* 上传本地模型和数据集特征大小 */
    @Transaction(intent = Transaction.TYPE.SUBMIT)
    public Model CreateModel(final Context ctx, final String model_weights,
            final String featureSize, final String t) {
        ChaincodeStub stub = ctx.getStub();
        String txid = stub.getTxId();
        String channelId = stub.getChannelId();

        // if (ModelExists(ctx, t)) {
        // String errorMessage = String.format("Model %s already exists", txid);
        // System.out.println(errorMessage);
        // throw new ChaincodeException(errorMessage,
        // AssetTransferErrors.ASSET_ALREADY_EXISTS.toString());
        // }

        Model model = Model.builder()
                .t(t)
                .model_weights(model_weights)
                .feature_size(featureSize)
                .channelId(channelId)
                .build();
        // Use Genson to convert the Asset into string, sort it alphabetically and
        // serialize it into a json string
        String sortedJson = genson.serialize(model);
        stub.putStringState(t, sortedJson);
        System.out.println("+++++" + sortedJson.length());

        return model;
    }

    @Transaction(intent = Transaction.TYPE.EVALUATE)
    public String GetAllAssets(final Context ctx) {
        ChaincodeStub stub = ctx.getStub();

        List<Model> queryResults = new ArrayList<Model>();

        // To retrieve all assets from the ledger use getStateByRange with empty
        // startKey & endKey.
        // Giving empty startKey & endKey is interpreted as all the keys from beginning
        // to end.
        // As another example, if you use startKey = 'asset0', endKey = 'asset9' ,
        // then getStateByRange will retrieve task with keys between asset0 (inclusive)
        // and asset9 (exclusive) in lexical order.
        QueryResultsIterator<KeyValue> results = stub.getStateByRange("", "");

        for (KeyValue result : results) {
            Model model = genson.deserialize(result.getStringValue(), Model.class);
            // System.out.println(model);
            queryResults.add(model);
        }

        final String response = genson.serialize(queryResults);

        return response;
    }

    /**
     * Retrieves all assets from the ledger.
     *
     * @param ctx the transaction context
     * @return array of assets found on the ledger
     */
    @Transaction(intent = Transaction.TYPE.EVALUATE)
    public List<Model> GetAllAssetsList(final Context ctx) {
        ChaincodeStub stub = ctx.getStub();

        List<Model> queryResults = new ArrayList<Model>();

        // To retrieve all assets from the ledger use getStateByRange with empty
        // startKey & endKey.
        // Giving empty startKey & endKey is interpreted as all the keys from beginning
        // to end.
        // As another example, if you use startKey = 'asset0', endKey = 'asset9' ,
        // then getStateByRange will retrieve task with keys between asset0 (inclusive)
        // and asset9 (exclusive) in lexical order.
        QueryResultsIterator<KeyValue> results = stub.getStateByRange("", "");
        for (KeyValue result : results) {
            System.out.println("1");
            Model model = genson.deserialize(result.getStringValue(), Model.class);
            // System.out.println(model);
            queryResults.add(model);
        }

        return queryResults;
    }

    /**
     * Checks the existence of the task on the ledger
     *
     * @param ctx the transaction context
     * @return boolean indicating the existence of the task
     */
    @Transaction(intent = Transaction.TYPE.EVALUATE)
    public boolean ModelExists(final Context ctx, final String t) {
        ChaincodeStub stub = ctx.getStub();
        String modelJSON = stub.getStringState(t);
        return (modelJSON != null && !modelJSON.isEmpty());
    }

    @Transaction(intent = Transaction.TYPE.EVALUATE)
    public String aggregateModels(Context ctx) {
        ChaincodeStub stub = ctx.getStub();
        QueryResultsIterator<KeyValue> results = stub.getStateByRange("", "");

        List<Map<String, Object>> modelList = new ArrayList<>();
        ObjectMapper objectMapper = new ObjectMapper();
        for (KeyValue result : results) {
            try {
                Map<String, Object> wrapper = objectMapper.readValue(result.getStringValue(), new TypeReference<>() {
                });
                // Map<String, Object> weights = (Map<String, Object>)
                // wrapper.get("model_weights");
                String modelWeightsJson = (String) wrapper.get("model_weights");
                Map<String, Object> weights = objectMapper.readValue(modelWeightsJson, new TypeReference<>() {
                });

                modelList.add(weights);
            } catch (IOException e) {
                throw new ChaincodeException("Failed to parse model JSON: " + e.getMessage());
            }
        }

        if (modelList.isEmpty()) {
            throw new ChaincodeException("No models found to aggregate.");
        }

        Map<String, Object> aggregated = new HashMap<>();
        int modelCount = modelList.size();

        for (String layer : modelList.get(0).keySet()) {
            Object firstValue = modelList.get(0).get(layer);

            if (firstValue instanceof List) {
                List<?> firstList = (List<?>) firstValue;
                if (!firstList.isEmpty() && firstList.get(0) instanceof List) {
                    // 处理二维数组
                    int rows = firstList.size();
                    int cols = ((List<?>) firstList.get(0)).size();

                    double[][] sum = new double[rows][cols];
                    for (Map<String, Object> model : modelList) {
                        List<List<Double>> weights = (List<List<Double>>) model.get(layer);
                        for (int i = 0; i < rows; i++) {
                            for (int j = 0; j < cols; j++) {
                                sum[i][j] += weights.get(i).get(j);
                            }
                        }
                    }

                    List<List<Double>> avg = new ArrayList<>();
                    for (int i = 0; i < rows; i++) {
                        List<Double> row = new ArrayList<>();
                        for (int j = 0; j < cols; j++) {
                            row.add(sum[i][j] / modelCount);
                        }
                        avg.add(row);
                    }

                    aggregated.put(layer, avg);
                } else {
                    // 处理一维数组
                    int len = firstList.size();
                    double[] sum = new double[len];

                    for (Map<String, Object> model : modelList) {
                        List<Double> weights = (List<Double>) model.get(layer);
                        for (int i = 0; i < len; i++) {
                            sum[i] += weights.get(i);
                        }
                    }

                    List<Double> avg = new ArrayList<>();
                    for (int i = 0; i < len; i++) {
                        avg.add(sum[i] / modelCount);
                    }
                    System.out.println(layer);
                    aggregated.put(layer, avg);
                }
            }
        }

        try {
            Map<String, Object> response = new HashMap<>();
            response.put("aggregated_weights", aggregated);
            return objectMapper.writeValueAsString(response);
        } catch (IOException e) {
            throw new ChaincodeException("Failed to serialize aggregated model: " + e.getMessage());
        }
    }

}
