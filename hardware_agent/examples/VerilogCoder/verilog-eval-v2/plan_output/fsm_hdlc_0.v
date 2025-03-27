module TopModule (
    input  logic clk,
    input  logic reset,
    input  logic in,
    output logic disc,
    output logic flag,
    output logic err
);

    // State definitions
    localparam IDLE = 3'b000,
               ONE = 3'b001,
               TWO = 3'b010,
               THREE = 3'b011,
               FOUR = 3'b100,
               FIVE = 3'b101,
               SIX = 3'b110,
               DISCARD = 3'b111,
               FLAG = 4'b1000,
               ERROR = 4'b1001;

    // State register
    logic [3:0] state, next_state;

    // Count register
    logic [2:0] count;

    // Sequential logic for state transition
    always @(posedge clk) begin
        if (reset) begin
            state <= IDLE;
            count <= 0;
        end else begin
            state <= next_state;
            if (in == 1'b1 && state != ERROR)
                count <= count + 1;
            else
                count <= 0;
        end
    end

    // Next state logic
    always @(*) begin
        next_state = state; // Default to hold state
        case (state)
            IDLE: next_state = in ? ONE : IDLE;
            ONE: next_state = in ? TWO : IDLE;
            TWO: next_state = in ? THREE : IDLE;
            THREE: next_state = in ? FOUR : IDLE;
            FOUR: next_state = in ? FIVE : IDLE;
            FIVE: next_state = in ? SIX : (in ? ERROR : DISCARD);
            SIX: next_state = in ? ERROR : FLAG;
            DISCARD: next_state = in ? ONE : IDLE;
            FLAG: next_state = in ? ONE : IDLE;
            ERROR: next_state = in ? ERROR : IDLE;
        endcase
    end

    // Output logic
    always @(*) begin
        disc = (state == DISCARD);
        flag = (state == FLAG);
        err = (state == ERROR);
    end

endmodule