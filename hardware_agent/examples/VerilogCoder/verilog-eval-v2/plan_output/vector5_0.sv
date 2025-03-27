`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	output logic a, b, c, d, e
);

	initial begin
		repeat(100) @(posedge clk, negedge clk)
			{a,b,c,d,e} <= $random;
		$finish;
	end
	
endmodule

module tb();

	typedef struct packed {
		int errors;
		int errortime;
		int errors_out;
		int errortime_out;

		int clocks;
	} stats;
	
	stats stats1;
	
	
	wire[511:0] wavedrom_title;
	wire wavedrom_enable;
	int wavedrom_hide_after_time;
	
	reg clk=0;
	initial forever
		#5 clk = ~clk;

	logic a;
	logic b;
	logic c;
	logic d;
	logic e;
	logic [24:0] out_ref;
	logic [24:0] out_dut;

	initial begin 
		$dumpfile("wave.vcd");
		$dumpvars();
	end


	wire tb_match;		// Verification
	wire tb_mismatch = ~tb_match;
	
	stimulus_gen stim1 (
		.clk,
		.* ,
		.a,
		.b,
		.c,
		.d,
		.e );
	RefModule good1 (
		.a,
		.b,
		.c,
		.d,
		.e,
		.out(out_ref) );
		
	TopModule top_module1 (
		.a,
		.b,
		.c,
		.d,
		.e,
		.out(out_dut) );

	
	bit strobe = 0;
	task wait_for_end_of_timestep;
		repeat(5) begin
			strobe <= !strobe;  // Try to delay until the very end of the time step.
			@(strobe);
		end
	endtask	

	
	final begin
		if (stats1.errors_out) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "out", stats1.errors_out, stats1.errortime_out);
		else $display("Hint: Output '%s' has no mismatches.", "out");

		$display("Hint: Total mismatched samples is %1d out of %1d samples\n", stats1.errors, stats1.clocks);
		$display("Simulation finished at %0d ps", $time);
		$display("Mismatches: %1d in %1d samples", stats1.errors, stats1.clocks);
	end
	
	// Verification: XORs on the right makes any X in good_vector match anything, but X in dut_vector will only match X.
	assign tb_match = ( { out_ref } === ( { out_ref } ^ { out_dut } ^ { out_ref } ) );
	// Use explicit sensitivity list here. @(*) causes NetProc::nex_input() to be called when trying to compute
	// the sensitivity list of the @(strobe) process, which isn't implemented.
	always @(posedge clk, negedge clk) begin

		stats1.clocks++;
		if (!tb_match) begin
			if (stats1.errors == 0) stats1.errortime = $time;
			stats1.errors++;
		end
		if (out_ref !== ( out_ref ^ out_dut ^ out_ref ))
		begin if (stats1.errors_out == 0) stats1.errortime_out = $time;
			stats1.errors_out = stats1.errors_out+1'b1; end

	end

   // add timeout after 100K cycles
   initial begin
     #1000000
     $display("TIMEOUT");
     $finish();
   end

endmodule



module RefModule (
  input a,
  input b,
  input c,
  input d,
  input e,
  output [24:0] out
);

  assign out = ~{ {5{a}}, {5{b}}, {5{c}}, {5{d}}, {5{e}} } ^ {5{a,b,c,d,e}};

endmodule


module TopModule
(
  input  logic a,
  input  logic b,
  input  logic c,
  input  logic d,
  input  logic e,
  output logic [24:0] out
);

  // Combinational logic for comparison between signal 'a' and itself
  assign out[24] = ~a ^ a;

  // Combinational logic for comparison between signal 'a' and signal 'b'
  assign out[23] = ~a ^ b;

  // Combinational logic for comparison between signal 'a' and signal 'c'
  assign out[22] = ~a ^ c;

  // Combinational logic for comparison between signal 'a' and signal 'd'
  assign out[21] = ~a ^ d;

  // Combinational logic for comparison between signal 'a' and signal 'e'
  assign out[20] = ~a ^ e;

  // Combinational logic for comparison between signal 'b' and signal 'a'
  assign out[19] = ~b ^ a;

  // Combinational logic for comparison between signal 'b' and itself
  assign out[18] = ~b ^ b;

  // Combinational logic for comparison between signal 'b' and signal 'c'
  assign out[17] = ~b ^ c;

  // Combinational logic for comparison between signal 'b' and signal 'd'
  assign out[16] = ~b ^ d;

  // Combinational logic for comparison between signal 'b' and signal 'e'
  assign out[15] = ~b ^ e;

  // Combinational logic for comparison between signal 'c' and signal 'a'
  assign out[14] = ~c ^ a;

  // Combinational logic for comparison between signal 'c' and signal 'b'
  assign out[13] = ~c ^ b;

  // Combinational logic for comparison between signal 'c' and itself
  assign out[12] = ~c ^ c;

  // Combinational logic for comparison between signal 'c' and signal 'd'
  assign out[11] = ~c ^ d;

  // Combinational logic for comparison between signal 'c' and signal 'e'
  assign out[10] = ~c ^ e;

  // Combinational logic for comparison between signal 'd' and signal 'a'
  assign out[9] = ~d ^ a;

  // Combinational logic for comparison between signal 'd' and signal 'b'
  assign out[8] = ~d ^ b;

  // Combinational logic for comparison between signal 'd' and signal 'c'
  assign out[7] = ~d ^ c;

  // Combinational logic for comparison between signal 'd' and itself
  assign out[6] = ~d ^ d;

  // Combinational logic for comparison between signal 'd' and signal 'e'
  assign out[5] = ~d ^ e;

  // Combinational logic for comparison between signal 'e' and signal 'a'
  assign out[4] = ~e ^ a;

  // Combinational logic for comparison between signal 'e' and signal 'b'
  assign out[3] = ~e ^ b;

  // Combinational logic for comparison between signal 'e' and signal 'c'
  assign out[2] = ~e ^ c;

  // Combinational logic for comparison between signal 'e' and signal 'd'
  assign out[1] = ~e ^ d;

  // Combinational logic for comparison between signal 'e' and itself
  assign out[0] = ~e ^ e;

endmodule