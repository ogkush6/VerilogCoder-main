module TopModule
(
  input  logic       clk,
  input  logic       reset,
  input  logic [7:0] in,
  output logic       done
);

  // State enum
  localparam IDLE  = 2'b00;
  localparam BYTE1 = 2'b01;
  localparam BYTE2 = 2'b10;
  localparam BYTE3 = 2'b11;

  // State register
  logic [1:0] state;
  logic [1:0] state_next;

  always @(posedge clk) begin
    if (reset)
      state <= IDLE;
    else
      state <= state_next;
  end

  // Next state combinational logic
  always @(*) begin
    state_next = state;
    case (state)
      IDLE:  state_next = (in[3] == 1'b1) ? BYTE1 : IDLE;
      BYTE1: state_next = BYTE2;
      BYTE2: state_next = BYTE3;
      BYTE3: state_next = (in[3] == 1'b1) ? BYTE1 : IDLE;
    endcase
  end

  // Output combinational logic
  always @(*) begin
    done = (state == BYTE3 && (state_next == IDLE || state_next == BYTE1)) ? 1'b1 : 1'b0;
  end

endmodule