module TopModule (
    input logic do_sub,
    input logic [7:0] a,
    input logic [7:0] b,
    output logic [7:0] out,
    output logic result_is_zero
);

always @(*) begin
    case (do_sub)
        0: out = a + b;
        1: out = a - b;
    endcase

    result_is_zero = ~|out; // Use bitwise negation and reduction AND operation to check if 'out' is zero
end

endmodule