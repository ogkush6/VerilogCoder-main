module TopModule
(
  input  logic p1a,
  input  logic p1b,
  input  logic p1c,
  input  logic p1d,
  input  logic p1e,
  input  logic p1f,
  input  logic p2a,
  input  logic p2b,
  input  logic p2c,
  input  logic p2d,
  output logic p1y,
  output logic p2y
);

  // Internal wire for the first AND operation
  logic p1_and1;
  // Internal wire for the second AND operation
  logic p1_and2;

  // Combinational logic for the first AND operation
  assign p1_and1 = p1a & p1b & p1c;
  // Combinational logic for the second AND operation
  assign p1_and2 = p1d & p1e & p1f;

  // Combinational logic for the OR operation
  assign p1y = p1_and1 | p1_and2;

  // Declare an internal wire for the AND operation between p2a and p2b
  logic p2_and1;
  assign p2_and1 = p2a & p2b;

  // Declare another internal wire for the AND operation between p2c and p2d
  logic p2_and2;
  assign p2_and2 = p2c & p2d;

  // Combinational logic for the OR operation
  assign p2y = p2_and1 | p2_and2;

endmodule