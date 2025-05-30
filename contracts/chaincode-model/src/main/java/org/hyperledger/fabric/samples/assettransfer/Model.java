package org.hyperledger.fabric.samples.assettransfer;

import com.owlike.genson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import org.hyperledger.fabric.contract.annotation.DataType;
import org.hyperledger.fabric.contract.annotation.Property;

@DataType()
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Model {
    // 用户标识
    @Property()
    private String t;

    @Property()
    private String model_weights;

    @Property()
    private String feature_size;

    @Property()
    private String channelId;
}