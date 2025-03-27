module TopModule
(
  input  logic       clk,
  input  logic       load,
  input  logic [511:0] data,
  output logic [511:0] q
);

  // Define a 512-bit register to hold the current state of the cells
  logic [511:0] state_reg;

  // Sequential logic to load the initial state of the cells from the input data when the load signal is asserted
  always @(posedge clk) begin
    if (load)
      state_reg <= data;
    else
      state_reg <= next_state;
  end

  // Define a 512-bit wire to compute the next state of each cell based on the XOR of its two neighbors
  logic [511:0] next_state;

  // Combinational logic to compute the next state of each cell
  assign next_state[0] = state_reg[1]; // For the first cell, the left neighbor is assumed to be 0
  assign next_state[511] = state_reg[510]; // For the last cell, the right neighbor is assumed to be 0
  genvar i;
  generate
    for (i = 1; i < 511; i = i + 1) begin
      assign next_state[i] = state_reg[i-1] ^ state_reg[i+1]; // For all other cells, the next state is the XOR of the two neighbors
    end
  endgenerate

  // Assign the state of the cells to the output
  assign q = state_reg;

endmodule