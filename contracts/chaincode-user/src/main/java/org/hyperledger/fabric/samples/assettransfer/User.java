/*
 * SPDX-License-Identifier: Apache-2.0
 */

package org.hyperledger.fabric.samples.assettransfer;

import java.util.Objects;

import org.hyperledger.fabric.contract.annotation.DataType;
import org.hyperledger.fabric.contract.annotation.Property;

import com.owlike.genson.annotation.JsonProperty;

@DataType()
public final class User {

    @Property()
    private final String userID;

    @Property()
    private final String password;

    @Property()
    private final String userType;

    @Property()
    private final String phoneNumber;

    @Property()
    private final String creditScore;

    @Property()
    private final String marginBalance;


    public String getPhoneNumber() {
        return phoneNumber;
    }

    public String getCreditScore() {
        return creditScore;
    }

    public String getMarginBalance() {
        return marginBalance;
    }

    public String getUserID() {
        return userID;
    }

    public String getPassword() {
        return password;
    }

    public String getUserType() {
        return userType;
    }

    public User(@JsonProperty("userID") final String userID, @JsonProperty("password") final String passWord, @JsonProperty("userType") final String userType,
                @JsonProperty("phoneNumber") final String phoneNumber, @JsonProperty("creditScore") final String creditScore,
                @JsonProperty("marginBalance") final String marginBalance) {
        this.userID = userID;
        this.password = passWord;
        this.userType = userType;
        this.phoneNumber = phoneNumber;
        this.creditScore = creditScore;
        this.marginBalance = marginBalance;
    }

    @Override
    public boolean equals(final Object obj) {
        if (this == obj) {
            return true;
        }

        if ((obj == null) || (getClass() != obj.getClass())) {
            return false;
        }

        User other = (User) obj;

        return Objects.deepEquals(
                new String[] {getUserID(), getUserType(), getPassword(), getPhoneNumber(), getCreditScore(), getMarginBalance()},
                new String[] {other.getUserID(), other.getUserType(), other.getPassword(), other.getPhoneNumber(), other.getCreditScore(), other.getMarginBalance()});
    }

    @Override public int hashCode() {
        return Objects.hash(userID, password, userType, phoneNumber, creditScore, marginBalance);
    }


    @Override
    public String toString() {
        return this.getClass().getSimpleName() + "@" + Integer.toHexString(hashCode()) + " [userID=" + userID  + ", password=" + password + ", userType=" + userType + ", phoneNumber=" + phoneNumber + ", creditScore=" + creditScore + ", marginBalance=" + marginBalance + "]";
    }
}
