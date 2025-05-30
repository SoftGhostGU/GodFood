package com.lcf.interceptor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

@Component
public class RequestLoggingInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        System.out.println("====== 请求信息 ======");
        System.out.println("时间: " + java.time.LocalDateTime.now());
        System.out.println("请求方法: " + request.getMethod() + "，请求路径: " + request.getRequestURI());
        return true; // 返回 true 表示继续执行后续处理
    }
}
