module TopModule
(
  input  logic [2:0] sel,
  input  logic [3:0] data0,
  input  logic [3:0] data1,
  input  logic [3:0] data2,
  input  logic [3:0] data3,
  input  logic [3:0] data4,
  input  logic [3:0] data5,
  output logic [3:0] out
);

  // Combinational logic for multiplexer

  always @(*) begin
    case (sel)
      3'b000: out = data0;
      3'b001: out = data1; 
      3'b010: out = data2; 
      3'b011: out = data3; 
      3'b100: out = data4; 
      3'b101: out = data5; 
      default: out = 4'b0000; // Implemented combinational logic to output 0 when sel is greater than 5.
    endcase
  end

endmodule