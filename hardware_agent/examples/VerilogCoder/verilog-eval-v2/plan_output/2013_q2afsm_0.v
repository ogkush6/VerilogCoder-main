module TopModule
(
  input  logic       clk,
  input  logic       resetn,
  input  logic [2:0] r,
  output logic [2:0] g
);

  // State encoding
  localparam STATE_A = 2'b00;
  localparam STATE_B = 2'b01;
  localparam STATE_C = 2'b10;
  localparam STATE_D = 2'b11;

  // State register
  logic [1:0] state;
  logic [1:0] state_next;

  // State transition logic
  always @(posedge clk) begin
    if (!resetn)
      state <= STATE_A;
    else
      state <= state_next;
  end

  // Next state combinational logic
  always @(*) begin
    case (state)
      STATE_A: begin
        if (r[0])
          state_next = STATE_B;
        else if (r[1])
          state_next = STATE_C;
        else if (r[2])
          state_next = STATE_D;
        else
          state_next = STATE_A;
      end
      STATE_B: begin
        if (r[0])
          state_next = STATE_B;
        else
          state_next = STATE_A;
      end
      STATE_C: begin
        if (r[1])
          state_next = STATE_C;
        else
          state_next = STATE_A;
      end
      STATE_D: begin
        if (r[2])
          state_next = STATE_D;
        else
          state_next = STATE_A;
      end
      default: state_next = STATE_A;
    endcase
  end

  // Output logic
  always @(*) begin
    g = 3'b000; // default value
    case (state)
      STATE_B: g[0] = 1'b1;
      STATE_C: g[1] = 1'b1;
      STATE_D: g[2] = 1'b1;
    endcase
  end
endmodule