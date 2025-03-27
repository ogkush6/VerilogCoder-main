module TopModule
(
  input  logic a,
  input  logic b,
  input  logic c,
  input  logic d,
  output logic out
);

// Output signal
assign out = (a == 0 && b == 1 && c == 0 && d == 0) ? 1'bx : 
             (a == 0 && b == 0 && c == 0 && d == 0) ? 1'b0 : 
             (a == 1 && b == 0 && c == 0 && d == 0) ? 1'b1 : 
             (a == 1 && b == 1 && c == 0 && d == 0) ? 1'b1 : 
             (a == 0 && b == 1 && c == 0 && d == 1) ? 1'b0 : 
             (a == 0 && b == 0 && c == 0 && d == 1) ? 1'b0 : 
             (a == 1 && b == 0 && c == 0 && d == 1) ? 1'bx : 
             (a == 1 && b == 1 && c == 0 && d == 1) ? 1'bx : 
             (a == 0 && b == 1 && c == 1 && d == 1) ? 1'b0 : 
             (a == 0 && b == 0 && c == 1 && d == 1) ? 1'b1 : 
             (a == 1 && b == 0 && c == 1 && d == 1) ? 1'b1 : 
             (a == 1 && b == 1 && c == 1 && d == 1) ? 1'b1 : 
             (a == 0 && b == 1 && c == 1 && d == 0) ? 1'b0 : 
             (a == 0 && b == 0 && c == 1 && d == 0) ? 1'b1 : 
             (a == 1 && b == 0 && c == 1 && d == 0) ? 1'b1 : 
             (a == 1 && b == 1 && c == 1 && d == 0) ? 1'b1 : 1'b0;

endmodule