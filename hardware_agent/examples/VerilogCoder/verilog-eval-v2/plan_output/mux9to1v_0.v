module TopModule
(
  input  logic [15:0] a,
  input  logic [15:0] b,
  input  logic [15:0] c,
  input  logic [15:0] d,
  input  logic [15:0] e,
  input  logic [15:0] f,
  input  logic [15:0] g,
  input  logic [15:0] h,
  input  logic [15:0] i,
  input  logic [3:0]  sel,
  output logic [15:0] out
);

  // Combinational logic for multiplexer
  always @(*) begin
    case(sel)
      4'b0000: out = a;
      4'b0001: out = b;
      4'b0010: out = c;
      4'b0011: out = d;
      4'b0100: out = e;
      4'b0101: out = f;
      4'b0110: out = g;
      4'b0111: out = h;
      4'b1000: out = i; // Added this line to select 'i' when 'sel' equals 8
      default: out = 16'b1111111111111111; // For the unused cases (sel=9 to 15), set all output bits to '1'
    endcase
  end
endmodule