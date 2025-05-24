/*
 * SPDX-License-Identifier: Apache-2.0
 */

package org.hyperledger.fabric.samples.assettransfer;


import java.util.ArrayList;
import java.util.List;

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


@Contract(
        name = "task",
        info = @Info(
                title = "Task Transfer",
                description = "The hyperlegendary task transfer",
                version = "0.0.1-SNAPSHOT",
                license = @License(
                        name = "Apache 2.0 License",
                        url = "http://www.apache.org/licenses/LICENSE-2.0.html"),
                contact = @Contact(
                        email = "a.transfer@example.com",
                        name = "Adrian Transfer",
                        url = "https://hyperledger.example.com")))
@Default
public final class TaskTransfer implements ContractInterface {

    private final Genson genson = new Genson();

    private enum AssetTransferErrors {
        ASSET_NOT_FOUND,
        ASSET_ALREADY_EXISTS
    }

    /**
     * Creates some initial assets on the ledger.
     *
     * @param ctx the transaction context
     */
    @Transaction(intent = Transaction.TYPE.SUBMIT)
    public void InitLedger(final Context ctx) {
        ChaincodeStub stub = ctx.getStub();
        JSONObject detail1 = new JSONObject();
        detail1.put("content", "我需要买感冒药和消炎药,送到普陀区1290号");
        detail1.put("money", "20元");
        detail1.put("deadline", "2023-8-24 12:00:05");
        detail1.put("area", "上海普陀区");
        JSONObject detail2 = new JSONObject();
        detail2.put("content", "打车，从静安大悦城到华东师范大学，两个人，无行李");
        detail2.put("money", "50元");
        detail2.put("deadline", "2023-8-25 11:00:05");
        detail2.put("area", "上海静安区");
        CreateAsset(ctx, detail2.toString(),  "lcf", "", "", "");
        CreateAsset(ctx, detail1.toString(),  "lcf", "", "", "");

    }


    /**
     * 创建资产
     *
     * @param ctx            ctx
     * @param taskDetail     任务细节
     * @param taskCreatorId  任务创建者id
     * @param taskReceiverId 任务接收id
     * @param receiveTime    收到时间
     * @param taskScore      任务分
     * @return {@link Task}
     */
    @Transaction(intent = Transaction.TYPE.SUBMIT)
    public Task CreateAsset(final Context ctx, final String taskDetail,
                            final String taskCreatorId, final String taskReceiverId, final String receiveTime, final String taskScore) {
        ChaincodeStub stub = ctx.getStub();
        String taskID = stub.getTxId();
        String channelId = stub.getChannelId();

        if (AssetExists(ctx, taskID)) {
            String errorMessage = String.format("Asset %s already exists", taskID);
            System.out.println(errorMessage);
            throw new ChaincodeException(errorMessage, AssetTransferErrors.ASSET_ALREADY_EXISTS.toString());
        }

        Task task = new Task(taskID, taskDetail, taskCreatorId, taskReceiverId, receiveTime, taskScore);
        // Use Genson to convert the Asset into string, sort it alphabetically and serialize it into a json string
        String sortedJson = genson.serialize(task);
        stub.putStringState(taskID, sortedJson);

        return task;
    }


    /**
     * 阅读资产
     *
     * @param ctx    ctx
     * @param taskID 任务id
     * @return {@link Task}
     */
    @Transaction(intent = Transaction.TYPE.EVALUATE)
    public Task ReadAsset(final Context ctx, final String taskID) {
        ChaincodeStub stub = ctx.getStub();
        String taskJSON = stub.getStringState(taskID);

        if (taskJSON == null || taskJSON.isEmpty()) {
            String errorMessage = String.format("Asset %s does not exist", taskID);
            System.out.println(errorMessage);
            throw new ChaincodeException(errorMessage, AssetTransferErrors.ASSET_NOT_FOUND.toString());
        }

        Task task = genson.deserialize(taskJSON, Task.class);
        return task;
    }


    /**
     * 更新资产
     *
     * @param ctx            ctx
     * @param taskID         任务id
     * @param taskDetail     任务细节
     * @param taskCreatorId  任务创建者id
     * @param taskReceiverId 任务接收id
     * @param receiveTime    收到时间
     * @param taskScore      任务分
     * @return {@link Task}
     */
    @Transaction(intent = Transaction.TYPE.SUBMIT)
    public Task UpdateAsset(final Context ctx, final String taskID, final String taskDetail,
                            final String taskCreatorId, final String taskReceiverId, final String receiveTime, final String taskScore) {
        ChaincodeStub stub = ctx.getStub();

        if (!AssetExists(ctx, taskID)) {
            String errorMessage = String.format("Asset %s does not exist", taskID);
            System.out.println(errorMessage);
            throw new ChaincodeException(errorMessage, AssetTransferErrors.ASSET_NOT_FOUND.toString());
        }

        Task newAsset = new Task(taskID, taskDetail, taskCreatorId, taskReceiverId, receiveTime, taskScore);
        // Use Genson to convert the Asset into string, sort it alphabetically and serialize it into a json string
        String sortedJson = genson.serialize(newAsset);
        stub.putStringState(taskID, sortedJson);
        return newAsset;
    }


    /**
     * 删除资产
     *
     * @param ctx    ctx
     * @param taskID 任务id
     */
    @Transaction(intent = Transaction.TYPE.SUBMIT)
    public void DeleteAsset(final Context ctx, final String taskID) {
        ChaincodeStub stub = ctx.getStub();

        if (!AssetExists(ctx, taskID)) {
            String errorMessage = String.format("Asset %s does not exist", taskID);
            System.out.println(errorMessage);
            throw new ChaincodeException(errorMessage, AssetTransferErrors.ASSET_NOT_FOUND.toString());
        }

        stub.delState(taskID);
    }

    /**
     * Checks the existence of the task on the ledger
     *
     * @param ctx the transaction context
     * @param taskID the ID of the task
     * @return boolean indicating the existence of the task
     */
    @Transaction(intent = Transaction.TYPE.EVALUATE)
    public boolean AssetExists(final Context ctx, final String taskID) {
        ChaincodeStub stub = ctx.getStub();
        String taskJSON = stub.getStringState(taskID);
        return (taskJSON != null && !taskJSON.isEmpty());
    }





    /**
     * Retrieves all assets from the ledger.
     *
     * @param ctx the transaction context
     * @return array of assets found on the ledger
     */
    @Transaction(intent = Transaction.TYPE.EVALUATE)
    public String GetAllAssets(final Context ctx) {
        ChaincodeStub stub = ctx.getStub();

        List<Task> queryResults = new ArrayList<Task>();

        // To retrieve all assets from the ledger use getStateByRange with empty startKey & endKey.
        // Giving empty startKey & endKey is interpreted as all the keys from beginning to end.
        // As another example, if you use startKey = 'asset0', endKey = 'asset9' ,
        // then getStateByRange will retrieve task with keys between asset0 (inclusive) and asset9 (exclusive) in lexical order.
        QueryResultsIterator<KeyValue> results = stub.getStateByRange("", "");

        for (KeyValue result: results) {
            Task task = genson.deserialize(result.getStringValue(), Task.class);
            System.out.println(task);
            queryResults.add(task);
        }

        final String response = genson.serialize(queryResults);

        return response;
    }

}
