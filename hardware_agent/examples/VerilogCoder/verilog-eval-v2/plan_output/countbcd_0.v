module TopModule (
    input clk,
    input reset,
    output [2:0] ena,
    output [15:0] q
);

    logic [3:0] ones_digit;
    logic [3:0] tens_digit;
    logic [3:0] hundreds_digit;
    logic [3:0] thousands_digit;

    assign q = {thousands_digit, hundreds_digit, tens_digit, ones_digit}; // Concatenation of digits

    assign ena[0] = (ones_digit == 4'b1001); // Enable signal for tens digit
    assign ena[1] = (tens_digit == 4'b1001) && ena[0]; // Enable signal for hundreds digit
    assign ena[2] = (hundreds_digit == 4'b1001) && ena[1]; // Enable signal for thousands digit

    always @(posedge clk) begin
        if (reset) begin
            ones_digit <= 4'b0000;
        end else begin
            if (ones_digit == 4'b1001) begin
                ones_digit <= 4'b0000;
            end else begin
                ones_digit <= ones_digit + 1'b1;
            end
        end
    end

    // Sequential logic for the tens digit counter
    always @(posedge clk) begin
        if (reset) begin
            tens_digit <= 4'b0000;
        end else if (ena[0]) begin
            if (tens_digit == 4'b1001) begin
                tens_digit <= 4'b0000; // Reset to 0 when tens digit reaches 9 and ena[0] is high
            end else begin
                tens_digit <= tens_digit + 1'b1; // Increment tens digit
            end
        end
    end

    // Sequential logic for the hundreds digit counter
    always @(posedge clk) begin
        if (reset) begin
            hundreds_digit <= 4'b0000;
        end else if (ena[1]) begin
            if (hundreds_digit == 4'b1001) begin
                hundreds_digit <= 4'b0000; // Reset to 0 when hundreds digit reaches 9 and ena[1] is high
            end else begin
                hundreds_digit <= hundreds_digit + 1'b1; // Increment hundreds digit
            end
        end
    end

    // Sequential logic for the thousands digit counter
    always @(posedge clk) begin
        if (reset) begin
            thousands_digit <= 4'b0000;
        end else if (ena[2]) begin
            if (thousands_digit == 4'b1001) begin
                thousands_digit <= 4'b0000; // Reset to 0 when thousands digit reaches 9 and ena[2] is high
            end else begin
                thousands_digit <= thousands_digit + 1'b1; // Increment thousands digit
            end
        end
    end

endmodule