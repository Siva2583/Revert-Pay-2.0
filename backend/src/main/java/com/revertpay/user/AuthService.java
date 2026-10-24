package com.revertpay.user;

import com.revertpay.account.Account;
import com.revertpay.account.AccountService;
import com.revertpay.account.OwnerType;
import com.revertpay.dto.LoginRequest;
import com.revertpay.dto.RegisterRequest;
import com.revertpay.security.JwtService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AccountService accountService;

    private final BCryptPasswordEncoder legacyBcrypt =
            new BCryptPasswordEncoder();

    public void register(RegisterRequest request) {

        if (userRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("Email already registered");
        }

        String hashedPassword =
                passwordEncoder.encode(request.getPassword());

        User user = new User(
                request.getName(),
                request.getEmail(),
                hashedPassword
        );

        user.setRole(request.getRole());

        User savedUser = userRepository.save(user);

        //System.out.println("USER SAVED: " + savedUser.getId());

        if (request.getRole() == Role.BUYER
                || request.getRole() == Role.SELLER) {

            accountService.createAccount(
                    OwnerType.USER,
                    savedUser.getId(),
                    "ACC" + savedUser.getId()
            );
        }

//        System.out.println(
//                "ACCOUNT CREATED: " + createdAccount.getAccountNumber()
//        );
    }

    public String verify(LoginRequest loginRequest) {

        User user = userRepository
                .findByEmail(loginRequest.getEmail())
                .orElseThrow(() ->
                        new RuntimeException("Invalid email or password")
                );

        String storedHash = user.getPassword();
        boolean passwordMatches;

        if (storedHash.startsWith("{bcrypt}")) {

            passwordMatches = passwordEncoder.matches(
                    loginRequest.getPassword(),
                    storedHash
            );

        } else if (storedHash.startsWith("{argon2}")) {

            passwordMatches = passwordEncoder.matches(
                    loginRequest.getPassword(),
                    storedHash
            );

        } else if (storedHash.startsWith("$2a$")
                || storedHash.startsWith("$2b$")
                || storedHash.startsWith("$2y$")) {

            // Legacy BCrypt hashes without a Spring Security prefix.
            passwordMatches = legacyBcrypt.matches(
                    loginRequest.getPassword(),
                    storedHash
            );

        } else {
            throw new RuntimeException("Invalid email or password");
        }

        if (!passwordMatches) {
            throw new RuntimeException("Invalid email or password");
        }

        // Upgrade a legacy BCrypt hash after successful verification.
        if (!storedHash.startsWith("{argon2}")) {
            user.setPassword(
                    passwordEncoder.encode(loginRequest.getPassword())
            );
            userRepository.save(user);
        }

        return jwtService.generateToken(user);
    }
}