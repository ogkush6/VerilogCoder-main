module TopModule
(
  input  logic clk,
  input  logic areset,
  input  logic train_valid,
  input  logic train_taken,
  output logic [1:0] state
);

  // 2-bit register for the state of the saturating counter
  logic [1:0] state_reg;
  logic [1:0] next_state;

  // Asynchronous reset
  always @(posedge clk or posedge areset) begin
    if (areset)
      state_reg <= 2'b01;
    else
      state_reg <= next_state;
  end

  // Logic to increment the counter
  always @(*) begin
    next_state = state_reg; // By default, keep the state unchanged
    if (train_valid) begin
      if (train_taken) begin
        if (state_reg < 3)
          next_state = state_reg + 1; // Increment the counter
        else
          next_state = 3; // Saturate at 3
      end
      else begin
        if (state_reg > 0)
          next_state = state_reg - 1; // Decrement the counter
        else
          next_state = 0; // Saturate at 0
      end
    end
  end

  assign state = state_reg;

endmodule