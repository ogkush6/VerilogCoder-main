module TopModule
(
  input  logic clk,
  input  logic reset,
  input  logic in,
  output logic done
);

  // State enum
  localparam IDLE  = 3'b000;
  localparam START = 3'b001;
  localparam DATA  = 3'b010;
  localparam STOP  = 3'b011;
  localparam ERROR = 3'b100;

  // State register
  logic [2:0] state;
  logic [2:0] state_next;

  // Data bit counter
  logic [3:0] bit_count;

  // Done signal register
  logic done_reg;

  always @(posedge clk) begin
    if (reset) begin
      state <= IDLE;
      bit_count <= 4'b0000;
      done_reg <= 1'b0;
    end else begin
      state <= state_next;
      if (state_next == DATA) begin
        if (bit_count == 4'b1000) begin
          bit_count <= 4'b0000;
        end else begin
          bit_count <= bit_count + 1;
        end
      end else if (state_next == IDLE || state_next == START) begin
        bit_count <= 4'b0000;
      end
      if (state == STOP && in == 1) begin
        done_reg <= 1'b1;
      end else begin
        done_reg <= 1'b0;
      end
    end
  end

  // Next state combinational logic
  always @(*) begin
    state_next = state;
    case (state)
      IDLE:  state_next = (in == 0) ? START : IDLE;
      START: state_next = DATA;
      DATA:  state_next = (bit_count == 4'b0111) ? STOP : DATA;
      STOP:  state_next = (in == 1) ? IDLE : ERROR;
      ERROR: state_next = (in == 1) ? IDLE : ERROR;
    endcase
  end

  // Output combinational logic
  assign done = done_reg;

endmodule