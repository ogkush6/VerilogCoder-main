module TopModule (
    input  logic      in,
    input  logic [9:0] state,
    output logic [9:0] next_state,
    output logic      out1,
    output logic      out2
);

    // Local signals for intermediate calculations
    logic [9:0] next_state_comb;

    // Combinational logic for next state
    always @(*) begin
        // Default assignment for next state
        next_state_comb = 10'b0;

        // State transitions for S0
        if (state[0]) begin
            next_state_comb[0] = ~in;
            next_state_comb[1] = in;
        end
        
        // State transitions for S1
        if (state[1]) begin
            next_state_comb[0] = ~in;
            next_state_comb[2] = in;
        end
        
        // State transitions for S2
        if (state[2]) begin
            next_state_comb[0] = ~in;
            next_state_comb[3] = in;
        end
        
        // State transitions for S3
        if (state[3]) begin
            next_state_comb[0] = ~in;
            next_state_comb[4] = in;
        end
        
        // State transitions for S4
        if (state[4]) begin
            next_state_comb[0] = ~in;
            next_state_comb[5] = in;
        end
        
        // State transitions for S5
        if (state[5]) begin
            next_state_comb[8] = ~in;
            next_state_comb[6] = in;
        end
        
        // State transitions for S6
        if (state[6]) begin
            next_state_comb[9] = ~in;
            next_state_comb[7] = in;
        end
        
        // State transitions for S7
        if (state[7]) begin
            next_state_comb[0] = ~in;
            next_state_comb[7] = in;
        end
        
        // State transitions for S8
        if (state[8]) begin
            next_state_comb[0] = ~in;
            next_state_comb[1] = in;
        end
        
        // State transitions for S9
        if (state[9]) begin
            next_state_comb[0] = ~in;
            next_state_comb[1] = in;
        end
    end

    // Assign the combinational result to the output
    assign next_state = next_state_comb;

    // Combinational logic for outputs
    always @(*) begin
        // Output logic for out1 and out2
        out1 = state[8] | state[9];
        out2 = state[7] | state[9];
    end

endmodule