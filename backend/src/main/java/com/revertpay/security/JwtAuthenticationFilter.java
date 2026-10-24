package com.revertpay.security;

import com.revertpay.user.User;
import com.revertpay.user.UserRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    private static final org.slf4j.Logger logger =
            org.slf4j.LoggerFactory.getLogger(JwtAuthenticationFilter.class);
    private final JwtService jwtService;
    private final UserRepository userRepository;

    public JwtAuthenticationFilter(
            JwtService jwtService,
            UserRepository userRepository
    ) {
        this.jwtService = jwtService;
        this.userRepository = userRepository;
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {

        String authHeader = request.getHeader("Authorization");

        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);

            try {
                if (jwtService.isTokenValid(token)) {
                    Long userId = jwtService.extractUserId(token);

                    Optional<User> userOptional =
                            userRepository.findById(userId);

                    if (userOptional.isPresent()
                            && SecurityContextHolder.getContext()
                            .getAuthentication() == null) {

                        User actualUser = userOptional.get();

                        SimpleGrantedAuthority authority =
                                new SimpleGrantedAuthority(
                                        "ROLE_" + actualUser.getRole().name()
                                );

                        UsernamePasswordAuthenticationToken authentication =
                                new UsernamePasswordAuthenticationToken(
                                        actualUser,
                                        null,
                                        List.of(authority)
                                );

                        SecurityContextHolder.getContext()
                                .setAuthentication(authentication);
                    }
                } else {
                    logger.warn(
                            "JWT validation failed for request: {}",
                            request.getRequestURI()
                    );
                }

            } catch (RuntimeException exception) {
                SecurityContextHolder.clearContext();

                logger.error(
                        "JWT authentication failed for request: {}",
                        request.getRequestURI(),
                        exception
                );
            }
        }

        filterChain.doFilter(request, response);
    }
}