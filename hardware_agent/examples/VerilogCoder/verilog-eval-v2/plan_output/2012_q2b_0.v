module TopModule (
  input logic [5:0] y,
  input logic w,
  output logic Y1,
  output logic Y3
);

  // Define the state types for the finite-state machine using one-hot encoding.
  wire state_A = y[0];
  wire state_B = y[1];
  wire state_C = y[2];
  wire state_D = y[3];
  wire state_E = y[4];
  wire state_F = y[5];

  // Logic for output Y1
  always @(*) begin
    // From state A, if w is 1, we go to state B
    Y1 = (state_A & w);  // Corrected to only check state A and w is 1
  end

  // Logic for output Y3
  always @(*) begin
    // From state B, if w is 0, we go to state D
    // From state C, if w is 0, we go to state D
    // From state E, if w is 0, we go to state D
    // From state F, if w is 0, we go to state D
    Y3 = (state_B & ~w) | (state_C & ~w) | (state_E & ~w) | (state_F & ~w);
  end

endmodule