package com.revertpay.user;

import com.revertpay.dto.LoginRequest;
import com.revertpay.dto.RegisterRequest;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    private final PasswordResetService passwordResetService;
    private final AuthService authService;
    public AuthController(
            AuthService authService,
            PasswordResetService passwordResetService
    ) {
        this.authService = authService;
        this.passwordResetService = passwordResetService;
    }

    @PostMapping("/register")
    public String register(
            @RequestBody @Valid RegisterRequest request
    ) {
        authService.register(request);
        return "User registered Successfully!!";
    }

    @PostMapping("/login")
    public String login(
            @RequestBody @Valid LoginRequest loginRequest
    ) {
        return authService.verify(loginRequest);
    }
    @PostMapping("/forgot-password")
    public String forgotPassword(@RequestBody java.util.Map<String, String> request) {

        String email = request.get("email");

        passwordResetService.requestPasswordReset(email);

        return "If an account exists with that email, password reset instructions will be sent.";
    }
    @PostMapping("/reset-password")
    public org.springframework.http.ResponseEntity<?> resetPassword(
            @RequestBody java.util.Map<String, String> request
    ) {
        try {
            passwordResetService.resetPassword(
                    request.get("token"),
                    request.get("newPassword")
            );

            return org.springframework.http.ResponseEntity.ok(
                    java.util.Map.of(
                            "message",
                            "Password reset successfully. You can now sign in."
                    )
            );

        } catch (IllegalArgumentException e) {
            return org.springframework.http.ResponseEntity.badRequest().body(
                    java.util.Map.of("message", e.getMessage())
            );
        }
    }
}