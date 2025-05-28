/*
 * SPDX-License-Identifier: Apache-2.0
 */

package org.hyperledger.fabric.samples.assettransfer;

import java.util.Objects;

import org.hyperledger.fabric.contract.annotation.DataType;
import org.hyperledger.fabric.contract.annotation.Property;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@DataType()
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public final class User {

    @Property()
    private String userID;
    @Property()
    private String userName;
    @Property()
    private String email;
    @Property()
    private String passWord;
    @Property()
    private String avatarUrl;
    @Property()
    private Integer age;
    @Property()
    private String gender;
    @Property()
    private Integer height_cm;
    @Property()
    private Integer weight_kg;
    @Property()
    private String hometown;
    @Property()
    private String occupation;
    @Property()
    private String education_level;
    @Property()
    private String marital_status;
    @Property()
    private String has_children;
    @Property()
    private String hobbies;
    @Property()
    private String diseases;
    @Property()
    private String dietary_preferences;
    @Property()
    private String activity_level;
    @Property()
    private String fitness_goals;
    @Property()
    private String food_allergies;
    @Property()
    private String cooking_skills;
    @Property()
    private Integer daily_food_budget_cny;

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
                new String[] { getUserID() },
                new String[] { other.getUserID() });
    }

    @Override
    public int hashCode() {
        return Objects.hash(userID, email, userName);
    }

    @Override
    public String toString() {
        return this.getClass().getSimpleName() + "@" + Integer.toHexString(hashCode()) + " [userID=" + userID
                + ", email=" + email + ", userName=" + userName + "]";
    }
}
