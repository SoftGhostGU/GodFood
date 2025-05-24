package com.lcf;


import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;

public class L2Test {

    public static void main(String[] args) {
        byte[] buffer = generateMessage((short) 324,(short) 40000);
        for(int i = 1; i <=buffer.length; i++) {
            System.out.printf("%x",buffer[i-1]);
            if(i%6==0){
                System.out.print(" ");
            }
        }
    }

    /**
     * 生成测试报文
     *
     * @param TelLength 消息长度
     * @param TelID     消息id
     * @return {@link byte} {@link []}
     */
    public static byte [] generateMessage(short TelLength,short TelID){
        ByteBuffer buffer = ByteBuffer.allocate(TelLength);
        buffer.order(ByteOrder.LITTLE_ENDIAN);
        buffer.putShort(TelLength);
        buffer.putShort(TelID);
        for( int i = 0 ; i < TelLength-4 ; i++)
        {
            buffer.put((byte)0);
        }

        return buffer.array();
    }

}
