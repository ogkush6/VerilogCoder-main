module TopModule (
  input logic clk,
  input logic [7:0] in,
  output logic [7:0] anyedge
);
  logic [7:0] in_prev;
  logic [7:0] anyedge_prev;

  always_ff @(posedge clk) begin
    in_prev <= in;
    anyedge_prev <= in ^ in_prev;
  end

  always_comb begin
    anyedge = anyedge_prev;
  end
endmodule