package com.lcf.pojo;

import lombok.Data;

@Data
public class Peer {
    private int Lpeer;
    private int weight;
    private int current;
    private String id;

    public Peer(){

    }

    public Peer(int Lpeer,int current,String id){
        this.id=id;
        this.Lpeer=Lpeer;
        this.current=current;
    }
}
