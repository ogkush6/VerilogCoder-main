module TopModule
(
  input  logic       clk,
  input  logic [7:0] in,
  output logic [7:0] pedge
);

  // Sequential logic
  logic [7:0] prev_in;
  logic [7:0] reg_pedge; // Register for storing intermediate signal

  always @( posedge clk ) begin
    prev_in <= in;
    reg_pedge <= temp_pedge; // Update the register every clock cycle
  end

  // Combinational logic
  logic [7:0] temp_pedge;

  always @(*) begin
    temp_pedge = (in & ~prev_in);
  end

  // Structural connections
  assign pedge = reg_pedge; // Connect the output to the register

endmodule