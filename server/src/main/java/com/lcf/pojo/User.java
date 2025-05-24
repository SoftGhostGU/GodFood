/*
 * SPDX-License-Identifier: Apache-2.0
 */

package com.lcf.pojo;
import com.alibaba.fastjson2.JSONObject;
import com.fasterxml.jackson.annotation.JsonProperty;

public final class User {


    private String userID;


    private String passWord;


    private String userType;


    private  String phoneNumber;


    private  String creditScore;


    private  String marginBalance;

    private String txId;

    private String channelId;


    public User(JSONObject prettyJson) {
        this.userID = prettyJson.get("userID").toString();
        this.passWord = prettyJson.get("password").toString();
        this.userType = prettyJson.get("userType").toString();
        this.phoneNumber = prettyJson.get("phoneNumber").toString();
        this.creditScore = prettyJson.get("creditScore").toString();
        this.marginBalance = prettyJson.get("marginBalance").toString();
    }


    public String getUserID() {
        return userID;
    }

    public void setUserID(String userID) {
        this.userID = userID;
    }

    public String getPassWord() {
        return passWord;
    }

    public void setPassWord(String passWord) {
        this.passWord = passWord;
    }

    public String getUserType() {
        return userType;
    }

    public void setUserType(String userType) {
        this.userType = userType;
    }

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public void setPhoneNumber(String phoneNumber) {
        this.phoneNumber = phoneNumber;
    }

    public String getCreditScore() {
        return creditScore;
    }

    public void setCreditScore(String creditScore) {
        this.creditScore = creditScore;
    }

    public String getMarginBalance() {
        return marginBalance;
    }

    public void setMarginBalance(String marginBalance) {
        this.marginBalance = marginBalance;
    }

    public String getTxId() {
        return txId;
    }

    public void setTxId(String txId) {
        this.txId = txId;
    }

    public String getChannelId() {
        return channelId;
    }

    public void setChannelId(String channelId) {
        this.channelId = channelId;
    }

    public User(@JsonProperty("userID") final String userID, @JsonProperty("password") final String password, @JsonProperty("userType") final String userType,
                @JsonProperty("phoneNumber") final String phoneNumber, @JsonProperty("creditScore") final String creditScore,
                @JsonProperty("marginBalance") final String marginBalance
    ) {
        this.userID = userID;
        this.passWord = password;
        this.userType = userType;
        this.phoneNumber = phoneNumber;
        this.creditScore = creditScore;
        this.marginBalance = marginBalance;
    }

}
