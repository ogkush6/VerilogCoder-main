module TopModule
(
  input  logic [15:0] scancode,
  output logic        left,
  output logic        down,
  output logic        right,
  output logic        up
);

  // Combinational logic for left arrow key
  always @(*) begin
    if (scancode == 16'he06b)
      left = 1'b1;
    else
      left = 1'b0;
  end

  // Combinational logic for down arrow key
  always @(*) begin
    if (scancode == 16'he072)
      down = 1'b1;
    else
      down = 1'b0;
  end

  // Combinational logic for right arrow key
  always @(*) begin
    if (scancode == 16'he074)
      right = 1'b1;
    else
      right = 1'b0;
  end

  // Combinational logic for up arrow key
  always @(*) begin
    if (scancode == 16'he075)
      up = 1'b1;
    else
      up = 1'b0;
  end
endmodule