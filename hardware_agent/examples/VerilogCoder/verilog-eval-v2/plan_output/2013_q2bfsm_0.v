module TopModule (
    input  logic clk,
    input  logic resetn,
    input  logic x,
    input  logic y,
    output logic f,
    output logic g
);

    // State identifiers
    localparam STATE_A = 3'b000;  // Initial state
    localparam STATE_B = 3'b001;  // Set f to 1 for one cycle
    localparam STATE_C = 3'b010;  // Monitor x for first 1
    localparam STATE_D = 3'b011;  // Monitor x for following 0
    localparam STATE_E = 3'b100;  // Monitor x for last 1
    localparam STATE_F = 3'b101;  // Set g to 1 and monitor y in first cycle
    localparam STATE_G = 3'b110;  // Monitor y in second cycle
    localparam STATE_H = 3'b111;  // Maintain g = 1 forever
    localparam STATE_I = 4'b1000; // Set g = 0 forever

    // State register
    logic [3:0] state;
    logic [3:0] state_next;

    // State transition logic
    always @(posedge clk) begin
        if (!resetn) begin
            state <= STATE_A;
        end else begin
            state <= state_next;
        end
    end

    // Next state logic
    always @(*) begin
        state_next = state; // Default to stay in the current state
        case (state)
            STATE_A: begin
                state_next = STATE_B;
            end
            STATE_B: begin
                state_next = STATE_C;
            end
            STATE_C: begin
                if (x == 1) begin
                    state_next = STATE_D;
                end
            end
            STATE_D: begin
                if (x == 0) begin
                    state_next = STATE_E;
                end
            end
            STATE_E: begin
                if (x == 1) begin
                    state_next = STATE_F;
                end else begin
                    state_next = STATE_C; // Go back to monitor first x=1
                end
            end
            STATE_F: begin
                if (y == 1) begin
                    state_next = STATE_H;
                end else begin
                    state_next = STATE_G;
                end
            end
            STATE_G: begin
                if (y == 1) begin
                    state_next = STATE_H;
                end else begin
                    state_next = STATE_I;
                end
            end
            STATE_H: begin
                // Maintain g = 1 forever
                state_next = STATE_H;
            end
            STATE_I: begin
                // Maintain g = 0 forever
                state_next = STATE_I;
            end
            default: begin
                state_next = STATE_A;
            end
        endcase
    end

    // Output logic
    always @(*) begin
        f = 0; // Default value for f
        g = 0; // Default value for g

        case (state)
            STATE_B: begin
                f = 1; // Set f to 1 for one cycle
            end
            STATE_F: begin
                g = 1; // Set g to 1 when entering STATE_F
            end
            STATE_G: begin
                g = 1; // Keep g at 1 during STATE_G
            end
            STATE_H: begin
                g = 1; // Maintain g = 1 forever
            end
            STATE_I: begin
                g = 0; // Maintain g = 0 forever
            end
        endcase
    end

endmodule