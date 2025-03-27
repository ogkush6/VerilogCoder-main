module TopModule (
    input  logic clk,
    input  logic reset,
    input  logic s,
    input  logic w,
    output logic z
);

    // State encoding
    localparam STATE_A  = 3'b000;
    localparam STATE_B  = 3'b001;
    localparam STATE_B1 = 3'b010;
    localparam STATE_B2 = 3'b011;
    localparam STATE_Z  = 3'b100;

    // State register
    logic [2:0] state;
    logic [2:0] state_next;

    // Previous w values
    logic pre_w, pre_pre_w;

    always @(posedge clk) begin
        if (reset) begin
            state <= STATE_A;
            pre_w <= 0;
            pre_pre_w <= 0;
        end else begin
            state <= state_next;
            pre_pre_w <= pre_w;
            pre_w <= w;
        end
    end

    // State transition logic
    always @(*) begin
        state_next = state; // Default to hold current state
        case (state)
            STATE_A: begin
                if (s == 1) begin
                    state_next = STATE_B;
                end else begin
                    state_next = STATE_A;
                end
            end
            STATE_B: begin
                state_next = STATE_B1;
            end
            STATE_B1: begin
                state_next = STATE_B2;
            end
            STATE_B2: begin
                if ((pre_pre_w & pre_w & !w) || (pre_pre_w & !pre_w & w) || (!pre_pre_w & pre_w & w)) begin
                    state_next = STATE_Z;
                end else begin
                    state_next = STATE_B;
                end
            end
            STATE_Z: begin
                state_next = STATE_B1;
            end
        endcase
    end

    // Output logic
    always @(*) begin
        z = (state == STATE_Z);
    end

endmodule