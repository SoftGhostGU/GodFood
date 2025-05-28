package com.lcf.dto;

import lombok.Getter;
import lombok.Setter;
import org.springframework.lang.Nullable;

import java.util.ArrayList;

public class ResponseDTO<T> {
    private Boolean success;
    @Nullable
    private T data;
    private int code;
    private String message;

    public ResponseDTO() {
        this.setSuccess(true);
        this.setCode(200);
        this.setMessage("成功");
        this.setData(null);
    }

    public ResponseDTO(T data) {
        this.setSuccess(true);
        this.setCode(200);
        this.setMessage("成功");
        this.setData(data);
    }

    public ResponseDTO(String message) {
        this.setSuccess(false);
        this.setCode(201);
        this.setMessage(message);
        this.setData(null);
    }

    public ResponseDTO(String message, T data) {
        this.setSuccess(false);
        this.setCode(201);
        this.setMessage(message);
        this.setData(data);
    }

    public ResponseDTO(int code, String message) {
        this.setSuccess(false);
        this.setCode(code);
        this.setMessage(message);
        this.setData(null);
    }

    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    @Nullable
    public T getData() {
        return data;
    }

    public void setData(@Nullable T data) {
        this.data = data;
    }

    public int getCode() {
        return code;
    }

    public void setCode(int code) {
        this.code = code;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

}
