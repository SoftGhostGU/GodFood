package com.lcf.security;

import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@EnableWebSecurity
public class WebSecurityConfig extends WebSecurityConfigurerAdapter {
    /**放行的路径*/
    public static final String[] PATH_RELEASE = {
//            "/login",
//            "/getUserAll",
//            "/register",
//            "/doc.html",
//            "/v3/api-docs/", "/webjars/", "/doc.html/", "/doc.html#/", "/swagger-ui/**"
            "/**"
    };

    @Override
    protected void configure(HttpSecurity httpSecurity) throws Exception {
        JWTAuthenticationFilter jwtAuthenticationFilter=new JWTAuthenticationFilter();
        httpSecurity.authorizeRequests()
                .and()
                .csrf().disable()
                .authorizeRequests()
                .antMatchers(PATH_RELEASE).permitAll()
                .anyRequest().authenticated()
                .and()
                .cors()
                .and()
                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
                .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS);
    }
}
