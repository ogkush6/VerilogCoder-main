module TopModule (
    input  logic clk,
    input  logic areset,
    input  logic bump_left,
    input  logic bump_right,
    input  logic ground,
    output logic walk_left,
    output logic walk_right,
    output logic aaah
);

    // State definitions
    localparam WALK_LEFT = 2'b00,
               WALK_RIGHT = 2'b01,
               FALL_LEFT = 2'b10,
               FALL_RIGHT = 2'b11;

    // State variables
    reg [1:0] state, next_state;

    // State transition logic with asynchronous reset
    always @(posedge clk or posedge areset) begin
        if (areset) begin
            state <= WALK_LEFT;
        end else begin
            state <= next_state;
        end
    end

    // Next state logic
    always @(*) begin
        case (state)
            WALK_LEFT: next_state = (bump_left && ground) ? WALK_RIGHT : (ground ? WALK_LEFT : FALL_LEFT);
            WALK_RIGHT: next_state = (bump_right && ground) ? WALK_LEFT : (ground ? WALK_RIGHT : FALL_RIGHT);
            FALL_LEFT: next_state = ground ? WALK_LEFT : FALL_LEFT;
            FALL_RIGHT: next_state = ground ? WALK_RIGHT : FALL_RIGHT;
            default: next_state = WALK_LEFT;
        endcase
    end

    // Output logic for aaah
    always @(*) begin
        aaah = (state == FALL_LEFT || state == FALL_RIGHT);
    end

    // Output logic for walking direction
    always @(*) begin
        walk_left = (state == WALK_LEFT);
        walk_right = (state == WALK_RIGHT);
    end

endmodule