module TopModule
(
  input  logic clk,
  input  logic areset,
  input  logic bump_left,
  input  logic bump_right,
  output logic walk_left,
  output logic walk_right
);

  // State enum
  localparam WALK_LEFT = 1'b0;
  localparam WALK_RIGHT = 1'b1;

  // State register
  logic state;
  logic state_next;

  // Implementing the state register
  always @(posedge clk or posedge areset) begin
    if (areset)
      state <= WALK_LEFT;
    else
      state <= state_next;
  end

  // Next state logic
  always @(*) begin
    state_next = state;
    if (bump_left && !bump_right)
      state_next = WALK_RIGHT;
    else if (!bump_left && bump_right)
      state_next = WALK_LEFT;
    else if (bump_left && bump_right)
      state_next = ~state;
  end

  // Output logic
  always @(*) begin
    if (state == WALK_LEFT) begin
      walk_left = 1'b1;
      walk_right = 1'b0;
    end
    else if (state == WALK_RIGHT) begin
      walk_left = 1'b0;
      walk_right = 1'b1;
    end
  end

endmodule