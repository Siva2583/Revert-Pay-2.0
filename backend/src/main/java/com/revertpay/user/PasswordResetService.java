package com.revertpay.user;

import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;

import java.security.MessageDigest;
import java.security.SecureRandom;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Base64;
import java.util.HexFormat;

@Service
@RequiredArgsConstructor
public class PasswordResetService {

    private final PasswordResetTokenRepository tokenRepository;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JavaMailSender mailSender;

    private final SecureRandom secureRandom = new SecureRandom();

    private String generateRawToken() {
        byte[] randomBytes = new byte[32];
        secureRandom.nextBytes(randomBytes);

        return Base64.getUrlEncoder()
                .withoutPadding()
                .encodeToString(randomBytes);
    }

    private String hashToken(String rawToken) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");

            byte[] hashBytes = digest.digest(
                    rawToken.getBytes(java.nio.charset.StandardCharsets.UTF_8)
            );

            return HexFormat.of().formatHex(hashBytes);

        } catch (java.security.NoSuchAlgorithmException e) {
            throw new IllegalStateException(
                    "SHA-256 is unavailable", e
            );
        }
    }

    private void sendResetEmail(String email, String rawToken) {

        String resetLink =
                "http://localhost:5173/reset-password?token=" + rawToken;

        SimpleMailMessage message = new SimpleMailMessage();

        message.setTo(email);
        message.setSubject("RevertPay Password Reset");
        message.setText(
                "Hello,\n\n"
                        + "We received a request to reset your RevertPay password.\n\n"
                        + "Use the link below to choose a new password:\n"
                        + resetLink + "\n\n"
                        + "This link expires in 15 minutes.\n"
                        + "If you did not request this reset, you can ignore this email."
        );

        mailSender.send(message);
    }

    private String createResetToken(User user) {

        String rawToken = generateRawToken();

        PasswordResetToken resetToken = new PasswordResetToken();
        resetToken.setUser(user);
        resetToken.setTokenHash(hashToken(rawToken));
        resetToken.setExpiresAt(
                Instant.now().plus(15, ChronoUnit.MINUTES)
        );
        resetToken.setUsed(false);

        tokenRepository.save(resetToken);

        return rawToken;
    }

    @Transactional
    public void requestPasswordReset(String email) {

        userRepository.findByEmail(email).ifPresent(user -> {

            // Invalidate earlier, unused reset tokens for this user.
            tokenRepository.invalidateUnusedTokensForUser(user.getId());

            String rawToken = createResetToken(user);

            sendResetEmail(user.getEmail(), rawToken);
        });
    }

    @Transactional
    public void resetPassword(String rawToken, String newPassword) {

        if (rawToken == null || rawToken.isBlank()) {
            throw new IllegalArgumentException("Reset token is required.");
        }

        if (newPassword == null || newPassword.length() < 8) {
            throw new IllegalArgumentException(
                    "Password must contain at least 8 characters."
            );
        }

        String tokenHash = hashToken(rawToken);

        PasswordResetToken resetToken =
                tokenRepository.findByTokenHash(tokenHash)
                        .orElseThrow(() -> new IllegalArgumentException(
                                "Invalid or expired reset link."
                        ));

        if (resetToken.isUsed()
                || !resetToken.getExpiresAt().isAfter(Instant.now())) {
            throw new IllegalArgumentException(
                    "Invalid or expired reset link."
            );
        }

        User user = resetToken.getUser();

        user.setPassword(passwordEncoder.encode(newPassword));
        userRepository.save(user);

        resetToken.setUsed(true);
        tokenRepository.save(resetToken);

        // Invalidate other unused tokens belonging to the same user.
        tokenRepository.invalidateUnusedTokensForUser(user.getId());
    }
}