module TopModule
(
  input  logic [99:0] a,
  input  logic [99:0] b,
  input  logic        sel,
  output logic [99:0] out
);

  // Combinational logic

  logic [99:0] out_mux;

  always @(*) begin
    out_mux = sel ? b : a;
  end

  // Structural connections

  assign out = out_mux;
endmodule