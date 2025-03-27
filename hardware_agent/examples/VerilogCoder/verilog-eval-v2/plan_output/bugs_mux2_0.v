module TopModule (
    input  logic       sel,
    input  logic [7:0] a,
    input  logic [7:0] b,
    output logic [7:0] out
);

    // Implement the logic for the 'out' signal
    assign out = sel ? a : b;

endmodule