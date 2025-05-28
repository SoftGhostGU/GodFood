/*
 * SPDX-License-Identifier: Apache-2.0
 */

package org.hyperledger.fabric.samples.assettransfer;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

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

@Contract(name = "user", info = @Info(title = "User Transfer", description = "The hyperlegendary user transfer", version = "0.0.1-SNAPSHOT", license = @License(name = "Apache 2.0 License", url = "http://www.apache.org/licenses/LICENSE-2.0.html"), contact = @Contact(email = "a.transfer@example.com", name = "Adrian Transfer", url = "https://hyperledger.example.com")))
@Default
public final class UserTransfer implements ContractInterface {

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
    }

    /**
     * Creates a new user on the ledger.
     *
     * @param ctx      the transaction context
     * @param userID   the ID of the new user
     * @param userType the userType of the new user
     * @return the created user
     */
    @Transaction(intent = Transaction.TYPE.SUBMIT)
    public String CreateUser(final Context ctx, final String email, final String userString) {
        ChaincodeStub stub = ctx.getStub();
        stub.putStringState(email, userString);
        return "User created successfully";
    }

    /**
     * Retrieves an user with the specified ID from the ledger.
     *
     * @param ctx   the transaction context
     * @param email the email of the user
     * @return the user found on the ledger if there was one
     */
    @Transaction(intent = Transaction.TYPE.EVALUATE)
    public String getUserByEmail(final Context ctx, final String email) {
        ChaincodeStub stub = ctx.getStub();
        String userJSON = stub.getStringState(email);

        if (userJSON == null || userJSON.isEmpty()) {
            String errorMessage = String.format("User with email %s does not exist", email);
            System.out.println(errorMessage);
            throw new ChaincodeException(errorMessage, AssetTransferErrors.ASSET_NOT_FOUND.toString());
        }

        return userJSON;
    }

    /**
     * 查询资产细节
     *
     * @param ctx    ctx
     * @param userID 用户id
     */
    @Transaction(intent = Transaction.TYPE.EVALUATE)
    public String ReadAssetDetail(final Context ctx, final String userID) {
        ChaincodeStub stub = ctx.getStub();

        String txId = stub.getTxId();
        String channelId = stub.getChannelId();
        if (txId == null || channelId == null) {
            String errorMessage = String.format("查询txid和channelId失败", ctx);
            System.out.println(errorMessage);
            throw new ChaincodeException(errorMessage, AssetTransferErrors.ASSET_NOT_FOUND.toString());
        }
        Map<String, String> resultMap = new HashMap<>();
        resultMap.put("channelId", channelId);
        resultMap.put("txId", txId);
        String result = resultMap.toString();
        return result;
    }

    /**
     * Updates the properties of an user on the ledger.
     *
     * @param ctx      the transaction context
     * @param userID   the ID of the user being updated
     * @param userType the userType of the user being updated
     * @return the transferred user
     */
    @Transaction(intent = Transaction.TYPE.SUBMIT)
    public String UpdateUser(final Context ctx, final String email, final String userString) {
        ChaincodeStub stub = ctx.getStub();
        stub.putStringState(email, userString);
        return "boolean";
    }

    /**
     * Checks the existence of the user on the ledger
     *
     * @param ctx    the transaction context
     * @param userID the ID of the user
     * @return boolean indicating the existence of the user
     */
    @Transaction(intent = Transaction.TYPE.EVALUATE)
    public boolean UserExists(final Context ctx, final String email) {
        ChaincodeStub stub = ctx.getStub();
        String userJSON = stub.getStringState(email);
        return (userJSON != null && !userJSON.isEmpty());
    }

    /**
     * Retrieves all assets from the ledger.
     *
     * @param ctx the transaction context
     * @return array of assets found on the ledger
     */
    @Transaction(intent = Transaction.TYPE.EVALUATE)
    public String GetAllUsers(final Context ctx) {
        ChaincodeStub stub = ctx.getStub();

        List<User> queryResults = new ArrayList<User>();

        // To retrieve all assets from the ledger use getStateByRange with empty
        // startKey & endKey.
        // Giving empty startKey & endKey is interpreted as all the keys from beginning
        // to end.
        // As another example, if you use startKey = 'asset0', endKey = 'asset9' ,
        // then getStateByRange will retrieve user with keys between asset0 (inclusive)
        // and asset9 (exclusive) in lexical order.
        QueryResultsIterator<KeyValue> results = stub.getStateByRange("", "");

        for (KeyValue result : results) {
            User user = genson.deserialize(result.getStringValue(), User.class);
            System.out.println(user);
            queryResults.add(user);
        }

        final String response = genson.serialize(queryResults);

        return response;
    }
}
