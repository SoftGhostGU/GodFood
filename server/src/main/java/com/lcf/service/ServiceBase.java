package com.lcf.service;

import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.lcf.blockchain.FabricBasic;
import com.lcf.pojo.Peer;
import io.grpc.netty.shaded.io.netty.channel.Channel;
import org.hyperledger.fabric.client.CloseableIterator;
import org.hyperledger.fabric.client.Contract;
import org.hyperledger.fabric.client.Gateway;
import org.hyperledger.fabric.client.Network;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class ServiceBase {

    private final Gson gson = new GsonBuilder().setPrettyPrinting().create();

    /**
     * 得到链代码名称
     *
     * @param chainCodeName 链代号
     * @return {@link String}
     */
    public String getChainCodeName(String chainCodeName) {
        return System.getenv().getOrDefault("CHAINCODE_NAME", "user");

    }

    /**
     * 得到通道名称
     *
     * @param channelName 通道名称
     * @return {@link String}
     */
    public String getChannelName(String channelName) {
        return System.getenv().getOrDefault("CHANNEL_NAME", "mychannel");
    }

    /**
     * 获取代表智能合约所在通道的部署的网络实例。
     *
     * @param gateway 网关
     * @return {@link Contract}
     */
    public Contract fetchContract(final Gateway gateway, String channelName, String chaincodeName) throws Exception {
        if (gateway == null || channelName == null || channelName.equals("") || chaincodeName == null
                || chaincodeName.equals("")) {
            throw new Exception("获取代表智能合约所在通道的部署的网络实例失败");
        }
        Network network = gateway.getNetwork(channelName);
        // 从网络中获取智能合约
        return network.getContract(chaincodeName);
    }

    /**
     * 加权轮询的，获取通道下的网络实例。
     *
     * @param gateway 网关
     * @return {@link Contract}
     */
    public Contract fetchContractByLoad(final Gateway gateway, String channelName, String chaincodeName)
            throws Exception {
        if (gateway == null || channelName == null || channelName.equals("") || chaincodeName == null
                || chaincodeName.equals("")) {
            throw new Exception("获取代表智能合约所在通道的部署的网络实例失败");
        }
        Network network = gateway.getNetwork(channelName);
        // 计算权重、选中对等节点
        calculateWeights();
        // 从网络中获取智能合约
        return network.getContract(chaincodeName);
    }

    /**
     * 负载计算
     * 
     * @return {@link Contract}
     */
    public void calculateWeights() {
        // 计算总负载
        int sum_current = FabricBasic.peers.stream()
                .mapToInt(Peer::getCurrent)
                .sum(); // 对这些属性值进行求和
        // 计算lpeer
        for (Peer peer : FabricBasic.peers) {
            int lpeer = (peer.getCurrent() == 0 ? Integer.MIN_VALUE : peer.getCurrent())
                    / (sum_current == 0 ? Integer.MIN_VALUE : sum_current);
            peer.setLpeer(lpeer);
        }
        // 计算分母
        int sumLpeer = 0;
        for (Peer peer : FabricBasic.peers) {
            int load = 1 / peer.getLpeer();
            sumLpeer = load;
        }
        for (Peer peer : FabricBasic.peers) {
            peer.setWeight(
                    (1 / peer.getLpeer()) / sumLpeer);
        }
        // 选中peer节点
        for (int i = FabricBasic.currentPeerId; i < FabricBasic.peers.size(); i++) {
            Peer peer = FabricBasic.peers.get(i);
            if (peer.getWeight() > FabricBasic.currentPeerId) {
                FabricBasic.currentPeerId = i;
            }
        }
    }

    /**
     * 转换为json
     *
     * @param json json
     * @return {@link String}
     */
    public JSONObject prettyJson(final byte[] json) {
        JSONObject resultObject = new JSONObject();
        String jsonStr = prettyJson(new String(json, StandardCharsets.UTF_8));
        try {
            resultObject = JSONObject.parseObject(jsonStr);
            return resultObject;
        } catch (Exception e) {
            resultObject.put("allAssert", JSONArray.parseArray(jsonStr));
            return resultObject;
        }
    }

    public String prettyJson(final String json) {
        JsonElement parsedJson = JsonParser.parseString(json);
        return gson.toJson(parsedJson);
    }
}
