module TopModule
(
  input  logic [7:0] a,
  input  logic [7:0] b,
  input  logic [7:0] c,
  input  logic [7:0] d,
  output logic [7:0] min
);

  // Combinational logic to find minimum of a and b

  logic [7:0] min_ab;

  always @(*) begin
    min_ab = (a < b) ? a : b;
  end

  // Combinational logic to find minimum of c and d

  logic [7:0] min_cd;

  always @(*) begin
    min_cd = (c < d) ? c : d;
  end

  // Combinational logic to find minimum of min_ab and min_cd

  always @(*) begin
    min = (min_ab < min_cd) ? min_ab : min_cd;
  end

endmodule