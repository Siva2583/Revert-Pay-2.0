package com.revertpay.dto;

import jakarta.validation.constraints.Digits;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;

@Getter
@Setter
@NoArgsConstructor
public class EscrowInitiateRequest {

    @NotBlank(message = "Seller account number is required")
    private String sellerAccountNumber;

    @NotBlank(message = "Item name is required")
    private String itemName;

    @NotNull(message = "Amount is required")
    @Positive(message = "Amount must be greater than zero")
    @Digits(
            integer = 12,
            fraction = 2,
            message = "Amount must have at most 12 integer digits and 2 decimal places"
    )
    private BigDecimal amount;
}

