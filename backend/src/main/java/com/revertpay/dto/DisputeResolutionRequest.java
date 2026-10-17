package com.revertpay.dto;

import com.revertpay.dispute.ResolutionType;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class DisputeResolutionRequest {

    private ResolutionType resolution;
}